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
from copy import deepcopy

import maya.cmds as mc
import maya.mel
from maya.OpenMaya import *

import ns.py as npy
import ns.py.Errors
import ns.py.Timer as Timer
import ns.maya.Progress as Progress

import ns.maya.msv as nmsv
import ns.maya.msv.SceneDescription as SceneDescription
import ns.maya.msv.AgentDescription as AgentDescription
import ns.maya.msv.MayaAgent as MayaAgent

def dagPathFromName( name ):
	selList = MSelectionList()
	MGlobal.getSelectionListByName( name, selList )
	if selList.isEmpty():
		raise npy.Errors.BadArgumentError("%s not found" % name)
	dagPath = MDagPath()
	selList.getDagPath( 0, dagPath )
	return dagPath
	
class MayaScene:
	def __init__(self):
		self.reset()
		
	def reset(self):
		self.sceneDesc = None
		self.geoMasters = {}
		self.clusterCache = {}
		self.primitiveCache = {}
		self.materialCache = {}
		self._geoMastersGroup = ""
		self._primitiveCacheGroup = ""
	
	def _getGeoMastersGroup( self ):
		if not self._geoMastersGroup:
			self._geoMastersGroup = mc.group( empty=True, name="geometryMasters" )
			self._geoMastersGroup = '|%s' % self._geoMastersGroup
		return self._geoMastersGroup
	
	def _getPrimitiveCacheGroup( self ):		
		if not self._primitiveCacheGroup:
			self._primitiveCacheGroup = mc.group( empty=True, name="msvPrimitives" )
			self._primitiveCacheGroup = '|%s' % self._primitiveCacheGroup
			mc.setAttr( "%s.visibility" % self._primitiveCacheGroup, False )
		return self._primitiveCacheGroup
	
	def importObj(self, file, groupName):
		'''Import and prep an obj file. This is used to import the terrain
		   object as well as the agent geometry objects.'''
		importedNodes = mc.file( file, returnNewNodes=True, type="OBJ", options='mo=0',
								 groupName=groupName, groupReference=True, i=True  )
		meshes = mc.ls( importedNodes, long=True, type="mesh" )
		for mesh in meshes:
			mc.polySoftEdge( mesh, a=180, ch=False )
			mc.polySubdivideFacet( mesh, divisions=0, ch=False )
		[newGroup] = mc.ls( importedNodes, long=True, assemblies=True )
		return newGroup

	def _chunkGeometry( self, msvGeometry, skin ):
		allWeights = msvGeometry.weights()
		if not allWeights:
			return
		
		[ shape ] = mc.listRelatives(skin.groupName, type='shape', fullPath=True, allDescendents=True)
		deformers = msvGeometry.deformers()
		faceGroups = [None] * len(deformers)
		numVerts = len(allWeights)
		dpMesh = dagPathFromName( shape )
		
		fMesh = MFnMesh( dpMesh )
		numFaces = fMesh.numPolygons()
		itFace = MItMeshPolygon( dpMesh )
		# For each vertex figure out which deformer influences
		# it the most. Associate the vertex's neighboring faces with
		# that deformer.
		#
		while not itFace.isDone():
			face = itFace.index()
			vertices = MIntArray()
			itFace.getVertices( vertices )

			maxWeight = 0
			primeDeformer = 0

			for i in range(len(deformers)):	
				weight = 0
				for j in range(vertices.length()):
					vtx = vertices[j]
					weight += allWeights[vtx][i]
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
		groupPrefix = len(skin.groupName)
		for i in range(len(faceGroups)):
			if not faceGroups[i]:
				continue
			[ newShape ] = mc.duplicate( shape )
			[ newShape ] = mc.ls( newShape, long=True )
			if len(faceGroups[i]) < numFaces:
				faceGroup = [ "%s.f[%d]" % (newShape, face) for face in faceGroups[i] ]
				mc.select( "%s.f[*]" % newShape, replace=True)
				mc.select( faceGroup, deselect=True )
				mc.delete()
			skin.addChunk(deformers[i], newShape)	
		mc.delete( mc.listRelatives( shape, parent=True, fullPath=True ) )
		
	def _buildGeoMaster( self, msvGeometry, groupName ):
		'''Called the first time a given .obj file is encountered.
		   Import the object and, if some sort of rigid skinning is
		   desired, chunk it up'''
		skin = MayaAgent.MayaSkin( group=self.importObj( msvGeometry.file, groupName ),
								   name=groupName,
								   parent=self._getGeoMastersGroup(),
								   master=True )
 
		if ( not msvGeometry.attach and
			 SceneDescription.eSkinType.smooth != self.sceneDesc.skinType ):
			self._chunkGeometry( msvGeometry, skin )
		
		return skin
	
	def _copyGeoMaster( self, skin, groupName, destGeometry ):
		copy = None
		if ( not destGeometry.skinnable() or
		     SceneDescription.eSkinType.smooth == self.sceneDesc.skinType ):
			# If the destination geometry is attached, has no skin weights,
			# or has weights and is to be smooth skinned - no chunking
			# is necessary so do a standard duplicate
			#
			#group = mc.duplicate( skin.groupName, name=groupName,
			#					  returnRootsOnly=True,
			#			  		  upstreamNodes=False, inputConnections=False )
			copy = skin.duplicate(groupName)
		elif SceneDescription.eSkinType.duplicate == self.sceneDesc.skinType:
			# destination geometry is skinnable and the user has chosen
			# to do a chunk skinning using chunk duplicates. Go through
			# the cached geometry, which should already be chunked, and
			# copy the chunks
			#
			copy = MayaAgent.MayaSkin( group=mc.group(empty=True),
									   name=groupName )
			
			for ( deformer, chunk ) in skin.chunks.items():
				chunk = skin.chunkName(chunk)
				newChunk = mc.duplicate( chunk, returnRootsOnly=True,
						  		  		 upstreamNodes=False, inputConnections=False )
				[newChunk] = mc.parent(newChunk, copy.groupName)
				[newChunk] = mc.ls(newChunk, long=True)
				copy.addChunk(deformer, newChunk)
		else:
			copy = MayaAgent.MayaSkin( group=mc.group(empty=True),
									   name=groupName )
			
			for ( deformer, chunk ) in skin.chunks.items():
				chunk = skin.chunkName(chunk)
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
				copy.addChunk(deformer, newChunk)

		destGeometry.skin = copy
	
	def importGeometry( self, mayaGeometry, groupName ):
		'''Build Maya geometry either by importing it from disk, or copying
		   an already imported geometry "master".'''
		key = ""
		if SceneDescription.eSkinType.smooth == self.sceneDesc.skinType:
			# When smooth binding every agent just gets a copy of the
			# .obj file geometry - so we can key the cache on the file
			# name and ignore the agent type
			#
			key = mayaGeometry.file()
		else:
			# When we are chunk binding, each agent type may chunk up the
			# geometry differently so we have to have one cache entry per
			# .obj file agent type combination
			#
			key = "%s_%s" % (mayaGeometry.agent.agentType(), mayaGeometry.file())
		if key in self.geoMasters:
			# "master" exists, copy it.
			self._copyGeoMaster( self.geoMasters[key], groupName, mayaGeometry )
		else:
			# no "master", create one, and then copy it.
			self.geoMasters[key] = self._buildGeoMaster( mayaGeometry.msvGeometry, groupName )
			self.importGeometry( mayaGeometry, groupName )

 	def buildPrimitive( self, mayaPrimitive ):
 		key = "%s_%s" % (mayaPrimitive.mayaJoint.agent.agentType(), mayaPrimitive.mayaJoint.msvName() )
 		master = ""
 		try:
 			master = self.primitiveCache[key]
 		except:
 			mayaPrimitive.build()
 			master = mayaPrimitive.name
 			[master] = mc.parent(master, self._getPrimitiveCacheGroup(), relative=True)
 			master = mc.rename( master, key )
 			[master] = mc.ls(master, long=True)
			self.primitiveCache[key] = master
		
		instance = ""
		if self.sceneDesc.instancePrimitives:
			# Use parent -add -noConnections instead of instance for
			# performance reasons. Maya is inherently inefficient in creating
			# instances, often approaching an n^2 runtime for adding a new
			# instance. Some of this overhead is due to reshuffling shading
			# connections every time a new instance is added. Using
			# -noConnections avoids this overhead but leaves the instances
			# unshaded. At the end of the import the shading connections will
			# be applied all at once.
			#
			[ shape ] = mc.listRelatives( master, fullPath=True, children=True )
			instance = mc.duplicate( master, parentOnly=True )
			[instance] = mc.parent( instance, world=True )
			mc.parent( shape, instance, addObject=True, noConnections=True, shape=True )
		else:
			instance = mc.duplicate( master )
			[instance] = mc.parent( instance, world=True )


		mayaPrimitive.name = mc.rename( instance, mayaPrimitive.baseName )
	
	def buildMaterial( self, material ):
		key = ""
		if material.colorMap:
			key = material.colorMap
		else:
			# Currently the only variation that is supported is in the
			# color map. If no color map is specified than it's safe
			# to assume that the id of the material will uniquely map
			# to a Maya shading group. (since the color map can vary
			# a material with a color map may actually map to several
			# Maya shading groups)
			#
			key = str(material.id())
		
		sg = ""
		try:
			sg = self.materialCache[key]
		except:
			# shadingNode doesn't work right in batch mode, so do it manually
			#
			shader = mc.createNode(self.sceneDesc.materialType, name=material.name())
			mc.connectAttr( "%s.msg" % shader, ":defaultShaderList1.s", nextAvailable=True)
			
			sg = mc.sets(renderable=True, empty=True, name="%sSG" % shader)
			mc.connectAttr( "%s.outColor" % shader, "%s.surfaceShader" % sg, force=True )	
			MayaAgent.setDouble3Attr( "%s.ambientColor" % shader, material.ambient )
			mc.setAttr( "%s.diffuse" % shader, material.diffuse )
			
			if "blinn" == self.sceneDesc.materialType:
				MayaAgent.setDouble3Attr( "%s.specularColor" % shader, material.specular )
				mc.setAttr( "%s.specularRollOff" % shader, material.roughness )			
			
			if material.colorMap:
				file = mc.createNode("file", name="%sFile" % shader)
				mc.connectAttr( "%s.msg" % file, ":defaultTextureList1.tx", nextAvailable=True)
				place = mc.createNode("place2dTexture", name="%sPlace" % shader)
				mc.connectAttr( "%s.msg" % place, ":defaultRenderUtilityList1.u", nextAvailable=True)
		
				mc.connectAttr( "%s.coverage" % place, "%s.coverage" % file, force=True )
				mc.connectAttr( "%s.translateFrame" % place, "%s.translateFrame" % file, force=True )
				mc.connectAttr( "%s.rotateFrame" % place, "%s.rotateFrame" % file, force=True )
				mc.connectAttr( "%s.mirrorU" % place, "%s.mirrorU" % file, force=True )
				mc.connectAttr( "%s.mirrorV" % place, "%s.mirrorV" % file, force=True )
				mc.connectAttr( "%s.stagger" % place, "%s.stagger" % file, force=True )
				mc.connectAttr( "%s.wrapU" % place, "%s.wrapU" % file, force=True )
				mc.connectAttr( "%s.wrapV" % place, "%s.wrapV" % file, force=True )
				mc.connectAttr( "%s.repeatUV" % place, "%s.repeatUV" % file, force=True )
				mc.connectAttr( "%s.offset" % place, "%s.offset" % file, force=True )
				mc.connectAttr( "%s.rotateUV" % place, "%s.rotateUV" % file, force=True )
				mc.connectAttr( "%s.noiseUV" % place, "%s.noiseUV" % file, force=True )
				mc.connectAttr( "%s.vertexUvOne" % place, "%s.vertexUvOne" % file, force=True )
				mc.connectAttr( "%s.vertexUvTwo" % place, "%s.vertexUvTwo" % file, force=True )
				mc.connectAttr( "%s.vertexUvThree" % place, "%s.vertexUvThree" % file, force=True )
				mc.connectAttr( "%s.vertexCameraOne" % place, "%s.vertexCameraOne" % file, force=True )
				mc.connectAttr( "%s.outUV" % place, "%s.uv" % file, force=True )
				mc.connectAttr( "%s.outUvFilterSize" % place, "%s.uvFilterSize" % file, force=True )
			
				mc.connectAttr( "%s.outColor" % file, "%s.color" % shader, force=True )

				mc.setAttr( "%s.fileTextureName" % file, "%s" % material.colorMap, type="string" )
			
			self.materialCache[key] = sg
		
		return sg

	def setClusterWeights( self, geometry, cluster ):
		# TODO: optimize the setAttrs so that the wl.w[x] attrs remain sparse
		mc.setAttr("%s.nw" % cluster, 0)
		clusterKey = geometry.file()
		if clusterKey in self.clusterCache:
			cachedCluster = self.clusterCache[clusterKey]
			mc.connectAttr( "%s.wl" % cachedCluster, "%s.wl" % cluster )
			mc.disconnectAttr( "%s.wl" % cachedCluster, "%s.wl" % cluster )
		else:
			weights = geometry.weights()
			numVerts = len(weights)
			for vtx in range(numVerts):
				attr = "%s.wl[%d].w" % (cluster, vtx)
				MayaAgent.setMultiAttr( attr, weights[vtx] )
			cachedCluster = mc.createNode("skinCluster")
			mc.connectAttr( "%s.wl" % cluster, "%s.wl" % cachedCluster )
			mc.disconnectAttr( "%s.wl" % cluster, "%s.wl" % cachedCluster )
			self.clusterCache[clusterKey] = cachedCluster
		mc.setAttr("%s.nw" % cluster, 1)
	
	def build(self, sceneDesc, progressRange):
		self.reset()
		self.sceneDesc = sceneDesc
		
		numAgents = self.sceneDesc.numAgents()
		
		# Calculate progress bar increments
		#
		terrainIncrement = int(0.1 * progressRange)
		shadingIncrement = 0
		if self.sceneDesc.loadPrimitives and self.sceneDesc.instancePrimitives:
			shadingIncrement = int(0.1 * progressRange)
		agentIncrement = 0
		simIncrement = 0
		cacheIncrement = 0
		deleteIncrement = 0
		if numAgents:
			leftover = progressRange - terrainIncrement - shadingIncrement
			
			if self.sceneDesc.cacheGeometry:
				cacheIncrement = int(0.35 * leftover)
				leftover -= cacheIncrement
			if self.sceneDesc.deleteSkeleton:
				deleteIncrement = int(0.05 * leftover) 
				leftover -= deleteIncrement
			
			agentIncrement = int(int(0.5 * leftover) / numAgents)
			simIncrement = int(int(0.5 * leftover) / numAgents)
		#
		# End of progress bar increment calculation
		
		if self.sceneDesc.terrainFile():
			self.importObj( self.sceneDesc.terrainFile(), "terrain" )
			
		mayaAgents = []
		startFrame = -1
		endFrame = -1
		
		for msvAgent in self.sceneDesc.agents():
			mayaAgent = MayaAgent.MayaAgent( msvAgent )
			
			Timer.push("Build Agent")
			Progress.setProgressStatus( "%s: Building..." % mayaAgent.name() )
			mayaAgent.build( self )
			Progress.advanceProgress( agentIncrement )
			Timer.pop()
			
			continue
				
			Timer.push("Sim Agent")
			Progress.setProgressStatus( "%s: Loading sim..." % mayaAgent.name() )
			mayaAgent.loadSim()
			
			# Presumably every agent will be simmed over the same frame
			# range - however since the frame ranges could conceivably
			# be different, find and and store the earliest startFrame
			# and latest endFrame
			#
			if mayaAgent.sim:
				if -1 == startFrame or mayaAgent.sim().startFrame < startFrame:
					startFrame = mayaAgent.sim().startFrame
				if -1 == endFrame or mayaAgent.sim().endFrame > endFrame:
					endFrame = mayaAgent.sim().endFrame
			
			Progress.advanceProgress( simIncrement )
			Timer.pop()
						
			mayaAgent.setupDisplayLayers()
			mayaAgents.append( mayaAgent )

		if self.sceneDesc.cacheGeometry:
			# Create geometry caches for each agent.
			#
			Timer.push("Caching Agents")
			Progress.setProgressStatus( "Caching..." )

			meshes = []
			for mayaAgent in mayaAgents:
				meshes.extend( [ geometry.shapeName() for geometry in mayaAgent.geometryData ] )
			
			cacheFileName = "%s_%s" % (sceneDesc.baseName(), sceneDesc.range)
			
			mc.cacheFile( directory=self.sceneDesc.cacheDir,
						  singleCache=True,
						  doubleToFloat=True,
						  format="OneFilePerFrame",
						  simulationRate=1,
						  sampleMultiplier=1,
						  fileName=cacheFileName,
						  startTime=startFrame,
						  endTime=endFrame,
						  points=meshes )
			switches = [ maya.mel.eval( 'createHistorySwitch( "%s", false )' % mesh ) for mesh in meshes ]
			switchAttrs = [ ( "%s.inp[0]" % switch ) for switch in switches ]
			mc.cacheFile( attachFile=True,
						  fileName=cacheFileName,
						  directory=self.sceneDesc.cacheDir,
						  channelName=meshes,
						  inAttr=switchAttrs )
			for switch in switches:
				mc.setAttr( "%s.playFromCache" % switch, True )
			Progress.advanceProgress( cacheIncrement )
			Timer.pop()
	
			if self.sceneDesc.deleteSkeleton:
				# After creating a geometry cache the skeleton, anim curves, and
				# skin clusters are no longer needed to playback the sim. To save
				# memory the user can choose to delete them.
				#
				Timer.push("Deleting Skeletons")
				Progress.setProgressStatus( "%s: Deleting skeleton..." % mayaAgent.name() )
				for mayaAgent in mayaAgents:
					mayaAgent.deleteSkeleton()
				Progress.advanceProgress( deleteIncrement )
				Timer.pop()

		if self.sceneDesc.loadPrimitives:
			if self.sceneDesc.instancePrimitives:
				# Add the shading assignments that were postponed by the use
				# of the -noConnections flag when creating the instances
				#
				Timer.push("Assign Primitive Shading")
				Progress.setProgressStatus( "Shading Primitives..." )
				masters = mc.listRelatives(self._getPrimitiveCacheGroup(), allDescendents=True)
				primitives = mc.ls( masters, allPaths=True, type="shape")
				mc.sets( primitives, edit=True, forceElement="initialShadingGroup" )
				Progress.advanceProgress( shadingIncrement )
				Timer.pop()
			else:
				mc.delete(self._getPrimitiveCacheGroup())
	
		# Clean up any "cache" nodes - nodes which were created only to
		# speed up the creation of other nodes by providing a source
		# to copy from
		#
		mc.delete(self._getGeoMastersGroup())
		for cluster in self.clusterCache.values():
			mc.delete(cluster)
		
		# The layers are off by default to speed up load, turn them on
		# now.
		#	
		MayaAgent.showLayers()


		
