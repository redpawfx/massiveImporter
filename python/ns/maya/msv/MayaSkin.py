# The MIT License
#	
# Copyright (c) 2008 James Piechota
#	
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import random
import re
import os.path

from maya.OpenMaya import *
import maya.cmds as mc
import maya.mel as mel

import ns.maya.msv.MayaUtil as MayaUtil
	
class eSkinType:
	smooth, duplicate, instance = range(3)

class MayaSkin:
	def __init__(self, group, name, skinType, parent=""):
		print >> sys.stderr, "MayaSkin"
		self.groupName = group
		self._shapeName = ""
		self._skinType = skinType
		self.chunks = {}
		
		if "|" == parent:
			# Parent to world
			[self.groupName] = mc.parent( self.groupName, world=True )
		elif "" != parent:
			# Parent to 'parent'
			[self.groupName] = mc.parent( self.groupName, parent, relative=True )
		# Try and set the name - if there's a name clash the actual
		# name may differ from 'name'. Store the actual name.
		self.groupName = mc.rename( self.groupName, name )
		[self.groupName] = mc.ls(self.groupName, long=True)
		# Find an store the shape name
		shapes = MayaUtil.getDescendentShapes( self.groupName )
		if shapes:
			self._shapeName = shapes[0][len(self.groupName) + 1:]
		
		print >> sys.stderr, "MayaSkin done"
	
	def copy(self, groupName, skinnable):
		if ( not skinnable or eSkinType.smooth == self._skinType ):
			# If the destination geometry is attached, has no skin weights,
			# or has weights and is to be smooth skinned - no chunking
			# is necessary so do a standard duplicate
			#
			group = mc.duplicate( self.groupName, name=groupName,
								  returnRootsOnly=True,
						  		  upstreamNodes=False, inputConnections=False )
			copy = MayaSkin( group=group,
							 name=groupName,
							 parent="|",
							 skinType=self._skinType )
		elif eSkinType.duplicate == self._skinType:
			# destination geometry is skinnable and the user has chosen
			# to do a chunk skinning using chunk duplicates. Go through
			# the cached geometry, which should already be chunked, and
			# copy the chunks
			#
			copy = MayaSkin( group=mc.group(empty=True),
							 name=groupName,
							 skinType=self._skinType )
			
			for ( deformer, chunk ) in self.chunks.items():
				chunk = self.chunkName(chunk)
				newChunk = mc.duplicate( chunk, returnRootsOnly=True,
						  		  		 upstreamNodes=False, inputConnections=False )
				[newChunk] = mc.parent(newChunk, copy.groupName)
				[newChunk] = mc.ls(newChunk, long=True)
				copy._addChunk(deformer, newChunk)
		else:
			copy = MayaSkin( group=mc.group(empty=True),
							 name=groupName,
							 skinType=self._skinType )
			
			for ( deformer, chunk ) in self.chunks.items():
				chunk = self.chunkName(chunk)
				[ shape ] = mc.listRelatives( chunk, fullPath=True, children=True )
				newChunk = mc.duplicate( chunk, parentOnly=True,
						  		  		 upstreamNodes=False, inputConnections=False )
				[newChunk] = mc.parent(newChunk, copy.groupName)
				[newChunk] = mc.ls(newChunk, long=True)
				# Use the noConnections flag for performance reasons: Maya can
				# spend a lot of time reshuffling instanced shading assignments.
				# Plus the material is applied after the geometry is created.
				#
				mc.parent( shape, newChunk, addObject=True, shape=True, noConnections=True )
				copy._addChunk(deformer, newChunk)	
		
		return copy	
	
	def createChunks(self, weights, deformers):
		'''Divide up the geometry into "chunks" where a chunk is the group of
		   vertices most strongly influenced by a given deformer.'''
		if not weights:
			return
		
		[ shape ] = mc.listRelatives(self.groupName,
									 type='shape',
									 fullPath=True,
									 allDescendents=True)
		faceGroups = [None] * len(deformers)
		numVerts = len(weights)
		dpMesh = MayaUtil.dagPathFromName(shape)
		
		fMesh = MFnMesh(dpMesh)
		numFaces = fMesh.numPolygons()
		itFace = MItMeshPolygon(dpMesh)
		# For each vertex figure out which deformer influences
		# it the most. Associate the vertex's neighboring faces with
		# that deformer.
		#
		while not itFace.isDone():
			face = itFace.index()
			vertices = MIntArray()
			itFace.getVertices(vertices)

			maxWeight = 0
			primeDeformer = 0

			for i in range(len(deformers)):	
				weight = 0
				for j in range(vertices.length()):
					vtx = vertices[j]
					weight += weights[vtx][i]
				if weight > maxWeight:
					maxWeight = weight
					primeDeformer = i
			
			# Associate all unassigned neighboring faces with
			# that deformer
			#
			if not faceGroups[primeDeformer]:
				faceGroups[primeDeformer] = []
			faceGroups[primeDeformer].append( face )
			itFace.next()
		
		# We now have a series of face groups each one associated
		# with a deformer. Chop up the original shape into these
		# face groups by duplicating the original object and removing
		# 
		groupPrefix = len(self.groupName)
		for i in range(len(faceGroups)):
			if not faceGroups[i]:
				continue
			[ newShape ] = mc.duplicate(shape)
			[ newShape ] = mc.ls(newShape, long=True)
			if len(faceGroups[i]) < numFaces:
				faceGroup = [ "%s.f[%d]" % (newShape, face) for face in faceGroups[i] ]
				mc.select( "%s.f[*]" % newShape, replace=True)
				mc.select( faceGroup, deselect=True )
				mc.delete()
			self._addChunk(deformers[i], newShape)	
		mc.delete(mc.listRelatives( shape, parent=True, fullPath=True ))
	
	def _addChunk(self, deformer, chunk):
		'''Strip out the group name from the chunk path. This assumes
		   that the chunk is a child of the group - which it should be'''
		self.chunks[deformer] = chunk[len(self.groupName) + 1:]

	def bindChunks(self, mayaAgent):
		if not self.chunks:
			print >> sys.stderr, "Warning: %s can not be bound because I was unable to chop it up into pieces." % geometry.name()
			return False
		
		for deformer in self.chunks.keys():
			# Chunks are stored with just the portion of the path below
			# the group - chunkName builds the full path
			#
			chunk = self.chunks[deformer]
			chunk = mc.parent( self.chunkName(chunk), mayaAgent.mayaJoint(deformer).name )
			[ chunk ] = mc.ls( chunk, long=True )
			self.chunks[deformer] = chunk
		return True
			

	def chunkName(self, chunk):
		if "|" == chunk[0] :
			return chunk
		else:
			return "%s|%s" % (self.groupName, chunk)

	def shapeName(self):
		return "%s|%s" % (self.groupName, self._shapeName)
