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

import ns.py.Timer as Timer

import ns.maya.msv.AgentDescription as AgentDescription
import ns.maya.msv.SceneDescription as SceneDescription
import ns.maya.msv.Agent as Agent

_animatable = ('rx', 'ry', 'rz', 'tx', 'ty', 'tz')
_rotateOrder2Enum = dict([['xyz', 0], ['yzx', 1], ['zxy', 2], ['xzy', 3], ['yxz', 4], ['zyx', 5]])	
_masterSegments = {}

def getDescendentShapes( name ):
	descendents = mc.listRelatives( name, allDescendents=True, fullPath=True )
	shapes = [ shape for shape in descendents if mc.objectType( shape, isAType="shape" ) ]	
	return shapes

def setMultiAttr( multiAttr, values, childAttr="" ):
	# Python allows a maximum of 255 arguments to a function/method call
	# so the maximum number of values we can process in a single setAttr
	# is 254 (255 minus 1 for the attribute name)
	chunkSize = min( 254, len(values) )
	if childAttr:
		childAttr = ".%s" % childAttr
	for chunk in range( 0, len(values), chunkSize ):
		# The last chunk may be smaller than chunkSize
		#
		curChunkSize = min( chunkSize, len(values) - chunk )
		
		stringValues = [ str(value) for value in values[chunk:chunk+curChunkSize] ]
		valString = ", ".join(stringValues)
		attr = "%s[%d:%d]%s" % (multiAttr, chunk, (chunk+curChunkSize-1), childAttr)
		eval('mc.setAttr( "%s", %s )' % (attr, valString))
		
		
def setMatrixAttr( matrixAttr, matrix ):
	'''Set a matrix attribute. This is always tricky because usually the matrix
	   data is stored in some sort of array structure, but Maya requires it to
	   be set as a comma-delimted list of values. Further complicated by the
	   fact that I haven't been able to get this to work using mc.setAttr(), so
	   have to fall back on calling the MEL setAttr command'''
	stringMatrix = [ str(value) for value in matrix ]
	arg = " ".join(stringMatrix)
	mel.eval('setAttr "%s" -type "matrix" %s' % (matrixAttr, arg))
	
def setDouble3Attr( double3Aattr, double3 ):
	'''Set a double3 attribute.'''
	stringDouble3 = [ str(value) for value in double3 ]
	arg = " ".join(stringDouble3)
	mel.eval('setAttr "%s" -type "double3" %s' % (double3Aattr, arg))

	
def hsvToRgb( hsv ):
	return mel.eval( 'hsv_to_rgb <<%f, %f, %f>>' % (hsv[0], hsv[1], hsv[2]) )

def rgbToHsv( rgb ):
	return mel.eval( 'rgb_to_hsv <<%f, %f, %f>>' % (rgb[0], rgb[1], rgb[2]) )

class MayaMaterial:
	def __init__(self, agent, material):
		self._agent = agent
		self._msvMaterial = material
		self.sgName = ""
		self.colorMap = material.rawColorMap
		self.specular = [ 0.0, 0.0, 0.0 ]
		self.ambient = [ 0.0, 0.0, 0.0 ]
		self.diffuse = 0.8
		self.roughness = 0.02
	
	def _resolveColor( self, msvColor, msvColorVar, msvColorSpace ):
		color = [ 0.0, 0.0, 0.0 ]
		for i in range(3):
			if msvColorVar[i]:
				# For now only the color map is allowed to vary. If a variable is
				# present elsewhere its default value will be used
				#
				color[i] = self._agent.variableValue( msvColorVar[i],
													  asInt=False,
													  varies=False )
			else:
				color[i] = msvColor[i]
		if msvColorSpace != "rgb":
			color = hsvToRgb( color )
		return color
		
	def id(self):
		return self._msvMaterial.id
	
	def name(self):
		if self.colorMap != self._msvMaterial.rawColorMap:
			basename = os.path.basename(self.colorMap)
			return os.path.splitext(basename)[0]
		elif self._msvMaterial.name:
			return self._msvMaterial.name
		else:
			return "%s%d" % (self._agent.sceneDesc().materialType, self.id())
		
	def build(self):
		self.colorMap = self._agent.replaceEmbeddedVariables( self.colorMap )
		
		self.specular = self._resolveColor( self._msvMaterial.specular,
											self._msvMaterial.specularVar,
											self._msvMaterial.specularSpace )
		self.ambient = self._resolveColor( self._msvMaterial.ambient,
											self._msvMaterial.ambientVar,
											self._msvMaterial.ambientSpace )
		# The V component Massive diffuse HSV color is represented as the
		# single 'diffuse' attribute in Maya.
		#
		diffuse = self._resolveColor( self._msvMaterial.diffuse,
									  self._msvMaterial.diffuseVar,
									  self._msvMaterial.diffuseSpace )
		diffuse = rgbToHsv( diffuse )
		self.diffuse = diffuse[2]
		
		if self._msvMaterial.roughnessVar:
			# For now only the color map is allowed to vary. If a variable is
			# present elsewhere its default value will be used
			#
			self.roughness = self._agent.variableValue( self._msvMaterial.roughnessVar,
														asInt=False,
														varies=False )
		else:
			self.roughness = self._msvMaterial.roughness
		
		#print "map: %s" % `self.colorMap`
		#print "specular: %s" % `self.specular`
		#print "ambient: %s" % `self.ambient`
		#print "diffuse: %s" % `self.diffuse`
		
		self.sgName = self._agent.mayaScene.buildMaterial( self )		

class MayaSkin:
	def __init__(self, group, name, parent=""):
		self.groupName = group
		self._shapeName = ""
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
		shapes = getDescendentShapes( self.groupName )
		if shapes:
			self._shapeName = shapes[0][len(self.groupName) + 1:]
	
	def addChunk(self, deformer, chunk):
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
			chunk = mc.parent( self.chunkName(chunk), mayaAgent.joint(deformer).name )
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

class MayaGeometry:
	def __init__(self, agent, geometry):
		self.agent = agent
		self.msvGeometry = geometry
		self.skin = None
	
	def name( self ):
		return self.skin.groupName
	
	def shapeName( self ):
		return self.skin.shapeName()
	
	def chunkNames( self ):
		if self.skin:
			return [ self.skin.chunkName( chunk ) for chunk in self.skin.chunks.values() ]
		else:
			return []
	
	def setName( self, name ):
		self.skin.groupName = name
	
	def attached( self ):
		return bool(self.msvGeometry.attach)
	
	def skinnable( self ):
		return not self.attached() and self.weights()
	
	def deformers( self ):
		return self.msvGeometry.deformers()

	def weights( self ):
		return self.msvGeometry.weights()
	
	def file( self ):
		return self.msvGeometry.file
	
	def build( self ):
		if not self.msvGeometry.file:
			# it is perfectly legal to have non-geometry:
			# a geometry node with no obj file. Massive just
			# doesn't display anything
			return

		# mo=0 makes causes multiple objects to be combined into one mesh
		# TODO: returnNewNodes is a relatively new flag (8.0? 8.5?) need something
		#		if this is to work with 7.0
		# TODO: maybe use namespaces? Or a better renaming prefix?
		if self.agent:
			self.agent.importGeometry( self, self.msvGeometry.name )
			if self.attached():
				[name] = mc.parent( self.name(), self.agent.joint(self.msvGeometry.attach).name )
				[name] = mc.ls( name, long=True )
				self.setName( name )
			if self.agent.sceneDesc().loadMaterials:
				mc.sets( self.name(), edit=True, forceElement=self.agent.material(self.msvGeometry.material).sgName )
			elif SceneDescription.eSkinType.instance == self.agent.sceneDesc().skinType:
				# When using chunk skinning with instances the newly
				# instanced chunks won't have any shading connections,
				# assign some now
				#
				mc.sets( self.name(), edit=True, forceElement="initialShadingGroup" )
			self.agent.registerGeometry( self )

class MayaAction:
	def __init__(self, agent, msvAction):
		self._msvAction = msvAction
		self._agent = agent
 	
 	def build( self ):
 		for channel in self._msvAction.curves.keys():
 			curve = self._msvAction.curves[channel]
 			tokens = channel.split()
 			if len(tokens) == 1:
 				object = self._agent.skelGroup
 				attr = tokens[0]
 			else:
  			 	object = self._agent.joint(tokens[0]).name
  			 	attr = tokens[1]

 			if not attr in _animatable:
 		 		# TODO: figure out how to handle non rot/trans attrs
 		 		continue
 		 	if object == self._agent.skelGroup:
 		 		# TODO: handle _agent animation... are these "agent curves"?
 		 		continue

 			baseValue = mc.getAttr("%s.%s" % (object, attr))
 			for key in curve.points:
 				mc.setKeyframe( object, attribute=attr,
								inTangentType="linear", outTangentType="linear",
								time=key[0] * self._msvAction.maxPoints, value=key[1] + baseValue)
 			
 		clip = mc.clip(self._agent.characterSet, startTime=0, endTime=self._msvAction.maxPoints, allRelative=True, scheduleClip=False)
 		mc.clip(self._agent.characterSet, name=clip, newName=self._msvAction.name)
 
class MayaPrimitive:
	def __init__(self, msvPrimitive, mayaJoint):
		self._msvPrimitive = msvPrimitive
		self.mayaJoint = mayaJoint
		self.baseName = (mayaJoint.msvJoint().name + "Segment")
		self.name = ""
		
	def create( cls, msvPrimitive, mayaJoint ):
		if isinstance( msvPrimitive, AgentDescription.Tube ):
			return MayaTube( msvPrimitive, mayaJoint )
		elif isinstance( msvPrimitive, AgentDescription.Sphere ):
			return MayaSphere( msvPrimitive, mayaJoint )
		elif isinstance( msvPrimitive, AgentDescription.Box ):
			return MayaBox( msvPrimitive, mayaJoint )
		elif isinstance( msvPrimitive, AgentDescription.Disc ):
			return MayaDisc( msvPrimitive, mayaJoint )
	create = classmethod(create)	
		
	def build(self):
		# Not sure why, but it seems necessary to set the segment rotate order
		# to the reverse of the joint rotate order
		#
		mc.setAttr((self.name + ".rotateOrder"), _rotateOrder2Enum[self.mayaJoint.rotateOrderString(True)])

		mc.setAttr((self.name + ".rotatePivot"), -self._msvPrimitive.centre[0], -self._msvPrimitive.centre[1], -self._msvPrimitive.centre[2])
		mc.setAttr((self.name + ".scalePivot"), -self._msvPrimitive.centre[0], -self._msvPrimitive.centre[1], -self._msvPrimitive.centre[2])
		mc.move(self._msvPrimitive.centre[0], self._msvPrimitive.centre[1], self._msvPrimitive.centre[2], self.name, objectSpace=True, relative=True)

		# TODO: this is actually just bone_rotate for now, later they may 
		# the actual rotate tag to contend with
		mc.xform(self.name, rotation=self._msvPrimitive.rotate, objectSpace=True, relative=True)

class MayaTube(MayaPrimitive):
	def __init__(self, msvPrimitive, mayaJoint):
		MayaPrimitive.__init__(self, msvPrimitive, mayaJoint)
		
	def build(self):
		[ self.name ] = mc.polyCylinder( radius=self._msvPrimitive.radius, height=self._msvPrimitive.length, 
								  		 axis=self._msvPrimitive.axis, 
								  		 subdivisionsX=10, subdivisionsY=1, subdivisionsZ=10, 
								  		 roundCap=True, ch=False, name=self.baseName )
		MayaPrimitive.build(self)
		

class MayaSphere(MayaPrimitive):
	def __init__(self, msvPrimitive, mayaJoint):
		MayaPrimitive.__init__(self, msvPrimitive, mayaJoint)

	def build(self):
		[ self.name ] = mc.polySphere( radius=self._msvPrimitive.radius, axis=self._msvPrimitive.axis, 
									   subdivisionsX=10, subdivisionsY=10, 
									   ch=False, name=self.baseName )
		MayaPrimitive.build(self)
	
class MayaBox(MayaPrimitive):
	def __init__(self, msvPrimitive, mayaJoint):
		MayaPrimitive.__init__(self, msvPrimitive, mayaJoint)

	def build(self):
		[ self.name ] = mc.polyCube( w=self._msvPrimitive.size[0], h=self._msvPrimitive.size[1], d=self._msvPrimitive.size[2],
									 ch=False, name=self.baseName )
		MayaPrimitive.build(self)
	
class MayaDisc(MayaPrimitive):
	def __init__(self, msvPrimitive, mayaJoint):
		MayaPrimitive.__init__(self, msvPrimitive, mayaJoint)

	def build(self):
		[ self.name ] = mc.polyCylinder( radius=self._msvPrimitive.radius, height=self._msvPrimitive.length, 
								  	  	 axis=self._msvPrimitive.axis, 
								  	  	 subdivisionsX=10, subdivisionsY=1, subdivisionsZ=10, 
								  	  	 roundCap=False, ch=False, name=self.baseName )
		MayaPrimitive.build(self)

class MayaJoint:
 	def __init__(self, agent, msvJoint):
 		self.agent = agent
 		self._msvJoint = msvJoint
 		self.primitive = None
 		self.name = ""
 		self.channelOffsets = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]

 	def msvJoint( self ):
 		return self._msvJoint
 	
 	def primitiveName( self ):
 		if self.primitive:
 			return "%s|%s" % (self.name, self.primitive.name)
 		else:
 			return ""

 	def isChannelFree( self, channel ):
 		return self._msvJoint.dof[channel]

 	def rotateOrderString( self, reversed ):
 		order = self._msvJoint.order
 		rotateOrder = ""
 		indices = []
 		if reversed:
 			indices = range(len(order) - 1, -1, -1)
 		else:
 			indices = range(len(order))
 		for i in indices:
 			if AgentDescription.kRX == order[i]:
 				rotateOrder += "x"
 			elif AgentDescription.kRY == order[i]:
 				rotateOrder += "y"
 			elif AgentDescription.kRZ == order[i]:
 				rotateOrder += "z"
 		return rotateOrder

 	def scale(self):
		if self._msvJoint.scaleVar:
			val = self.agent.variableValue(self._msvJoint.scaleVar, False)
			mc.scale( val, val, val, self.name )
			
	def setChannelOffsets(self):
		'''Treat the current translate values as the base translation. Any
		   translate animation applied will be relative to these values.'''
		[baseTranslate] = mc.getAttr("%s.translate" % self.name)
		self.channelOffsets[AgentDescription.channel2Enum["tx"]] = baseTranslate[0]
 		self.channelOffsets[AgentDescription.channel2Enum["ty"]] = baseTranslate[1]
 		self.channelOffsets[AgentDescription.channel2Enum["tz"]] = baseTranslate[2]
 	 	
 	def build(self):
 		self.name = mc.createNode("joint", name=self._msvJoint.name)
 
  		mc.setAttr((self.name + ".rotateOrder"), _rotateOrder2Enum[self.rotateOrderString(False)])
 
 		if self._msvJoint.translate:
			mc.move( self._msvJoint.translate[0], self._msvJoint.translate[1], self._msvJoint.translate[2],
					 self.name, objectSpace=True, relative=True )
		
		if self._msvJoint.transform:
			mc.xform( self.name, matrix=self._msvJoint.transform, objectSpace=True, relative=True)
			
 		# Use the 'joint' command to set the rotation degrees of freedom.
		# However since joints don't have a built-in concept of translation
		# degrees of freedom, just lock the translate channel attributes
		#
		#rdof = "%s%s%s" % (dof['rx'], dof['ry'], dof['rz'])
		#mc.joint( joint, e=True, dof=rdof )

		#for tdof in ( 'tx', 'ty', 'tz' ):
			# Only lock of the entry is ""
			#lock = not bool(dof[tdof])
			#mc.setAttr( joint + '.' + tdof, lock=lock )
 	
 		if self._msvJoint.parent:
 			[self.name] = mc.parent(self.name, self.agent.joint(self._msvJoint.parent).name, relative=True)
 			[self.name] = mc.ls(self.name, long=True)
  	
		# Need to zero out the transform so that actions are applied correctly.
		# Unfortunately this also causes us to lose the existing transform info
		# when we export back to massive we may need this transform info...
		# TODO: how to keep/recover the transformation information? Another way
		# to support actions besides zeroing out the transformation information?
		mc.makeIdentity(self.name, apply=True, translate=True, rotate=True)
		self.setChannelOffsets()
 		
		if not self.agent.rootJoint:
			self.agent.registerRootJoint( self )
			
	def buildPrimitive( self ):
		self.primitive = MayaPrimitive.create( self._msvJoint.primitive, self )
		self.agent.mayaScene.buildPrimitive( self.primitive )

		# Primitives are created after freezing transforms on the agent group
		# To make sure they are also scaled up by the agent heigh, manually
		# scale them here. For skinning reasons, the individual joint scales
		# are applied later, so we don't have to account for them here.
		#
		if self.agent.agentDesc().scaleVar:
			val = self.agent.variableValue( self.agent.agentDesc().scaleVar, False )
			mc.scale( val, val, val, self.primitive.name )

		[ self.primitive.name ] = mc.parent(self.primitive.name, self.name, relative=True)
		
		self.agent.registerPrimitive( self.primitive )

kPrimitiveLayerName = 'msvPrimitiveLayer'
kGeometryLayerName = 'msvGeometryLayer'
kSkeletonLayerName = 'msvSkeletonLayer'

def _getLayer( layerName, create ):
	'''Convenience method to get, and create if necessary, one of
	   Massive layers'''
	layer = ""
	layers = mc.ls( layerName, type="displayLayer" )
	if create and not layers:
		layers = [ mc.createDisplayLayer(name=layerName, empty=True) ]
		mc.setAttr( "%s.visibility" % layers[0], False )
	if layers:
		layer = layers[0]
	return layer

def getPrimitiveLayer():
	return _getLayer( kPrimitiveLayerName, True )

def getGeometryLayer():
	return _getLayer( kGeometryLayerName, True )

def getSkeletonLayer():
	return _getLayer( kSkeletonLayerName, True )


def showLayers():
	layers = []
	layers.append(_getLayer( kPrimitiveLayerName, False ))
	layers.append(_getLayer( kGeometryLayerName, False ))
	layers.append(_getLayer( kSkeletonLayerName, False ))
	for layer in layers:
		if layer:
			mc.setAttr( "%s.visibility" % layer, True )

	

# Node definition
class MayaAgent:
	def __init__(self, msvAgent):
		self.reset()
		self._msvAgent = msvAgent
	
	def reset(self):
		self.mayaScene = None
		self._msvAgent = None
		self._agentGroup = ""
		self.skelGroup = ""
		self.rootJoint = None
		self.geometryData = []
		self.materialData = []
		self.primitiveData = []
		self._zeroPose = ""
		self._bindPose = ""
		self.characterSet = ""

		self.joints = {}
		self.actions = {}

	def name( self ):
		return self._msvAgent.name

	def sceneDesc( self ):
		return self.mayaScene.sceneDesc
	
	def agentDesc( self ):
		return self._msvAgent.agentDesc
	
	def sim( self ):
		return self._msvAgent.sim()

	def agentType( self ):
		return self.agentDesc().agentType

	def variableValue( self, variableName, asInt=False, varies=True ):
		return self._msvAgent.variableValue( variableName, asInt, varies )

	def replaceEmbeddedVariables( self, s ):
		return self._msvAgent.replaceEmbeddedVariables( s )

	def importGeometry( self, mayaGeometry, groupName ):
		return self.mayaScene.importGeometry( mayaGeometry, groupName )

	def joint( self, msvJoint ):
		return self.joints[ msvJoint ]
	
	def material( self, id ):
		'''Return the MayaMaterial with the given ID. Create the MayaMaterial
		   from the Massive Material if needed. This guarantees that we only
		   create materials for geometry that is actually used.'''
		if id >= len(self.materialData):
			self.materialData.extend( [None] * ((id + 1) - len(self.materialData)) )
		if not self.materialData[id]:
			mayaMaterial = MayaMaterial( self, self.agentDesc().materialData[id]  )
			self.materialData[id] = mayaMaterial
			mayaMaterial.build()

		return self.materialData[id]
	
	def getAgentGroup( self ):
		if not self._agentGroup:
			self._agentGroup = mc.group( empty=True, name=self.name() )
			if self.agentDesc().scaleVar:
				val = self.variableValue( self.agentDesc().scaleVar, False )
				mc.scale( val, val, val, self._agentGroup )
			self._agentGroup = '|%s' % self._agentGroup
		return self._agentGroup

	def registerPrimitive( self, primitive ):
		self.primitiveData.append(primitive)
	
	def registerGeometry( self, geometry ):
		self.geometryData.append(geometry)
		# if the geometry is attached it will already be parented to a
		# joint. And if we are chunk skinning using instances the geometry
		# should stay under the master group.
		#
		if not geometry.attached() and \
		   SceneDescription.eSkinType.instance != self.sceneDesc().skinType:
			[name] = mc.parent(geometry.name(), self.getAgentGroup(), relative=True)
 			[name] = mc.ls(name, long=True)
 			geometry.setName(name)
 	
	def registerRootJoint( self, rootJoint ):
		assert not self.skelGroup
		self.rootJoint = rootJoint
		self.skelGroup = mc.group(self.rootJoint.name, name=self.name(), parent=self.getAgentGroup(), relative=True)
		self.skelGroup = "%s|%s" % (self.getAgentGroup(), self.skelGroup)
		# Group was just created so self.rootJoint is guaranteed to be the
		# only child
		#
		[self.rootJoint.name] = mc.listRelatives( self.skelGroup, children=True, fullPath=True )

	def setupDisplayLayers( self ):
		if self.rootJoint:
			mc.editDisplayLayerMembers( getSkeletonLayer(), self.rootJoint.name )
		for geometry in self.geometryData:
			chunks = geometry.chunkNames()
			if chunks:
				mc.editDisplayLayerMembers( getGeometryLayer(), chunks )
			else:
				mc.editDisplayLayerMembers( getGeometryLayer(), geometry.name() )
		for primitive in self.primitiveData:
			mc.editDisplayLayerMembers( getPrimitiveLayer(), primitive.name )

	def applyActions(self):
 		# The rotation order needed to build the skeleton does not apply
 		# to the animation - it is assumed to be xyz
 		#
 		for joint in self.joints.values():
 			mc.setAttr("%s.rotateOrder" % joint.name, _rotateOrder2Enum['xyz'])

		for msvAction in self.agentDesc().actions.values():
 	 		mc.dagPose(self._zeroPose, restore=True)
 	 		mayaAction = MayaAction( self, msvAction )
 	 		self.actions[msvAction.name] = mayaAction
 	 		mayaAction.build()

 	def scaleJoints(self):
 		for joint in self.joints.values():
 			joint.scale()
 			
  	def freezeAgentScale(self):
  		'''Make sure the agent scale doesn't also scale the translate values of
		   the sim data. We have to freeze the transform here since we won't
		   be allowed to after binding the skin'''
	
	  	# Freezing the root node's transform may update the translate values
	  	# of any/all joints in the skeleton, store those new translations as
	  	# the base values.
	  	#
  		mc.makeIdentity( self.getAgentGroup(), apply=True, translate=True, rotate=True, scale=True, normal=0 )
 		for joint in self.joints.values():
 			joint.setChannelOffsets()

  		
 	def buildCharacterSet(self):
 		setMembers = [ "%s.%s" % (joint.name, attr) for joint in self.joints.values() for attr in _animatable ]
 		self.characterSet = mc.character(setMembers, name=("%sCharacter" % self.name()))
 
	def buildSkeleton(self):
		for msvJoint in self.agentDesc().jointData:
			if not msvJoint:
				# some ids may not be used (e.g. 0)
				continue
			mayaJoint = MayaJoint( self, msvJoint )
			self.joints[msvJoint.name] = mayaJoint
			mayaJoint.build()
			
	def buildPrimitives(self):
		for joint in self.joints.values():
			joint.buildPrimitive()
					
	def buildGeometry( self ):
		for msvGeometry in AgentDescription.GeoIter( self.agentDesc().geoDB, self ):
			if not msvGeometry:
				# some ids may not be used (e.g. 0)
				continue
			mayaGeometry = MayaGeometry( self, msvGeometry )
			mayaGeometry.build()
 
  	def setBindPose( self ):
 		# The bind pose is stored in frame 1
 		if not self.agentDesc().bindPoseData:
 			return
 	
 		for jointSim in self.agentDesc().bindPoseData.joints():
 			mayaJoint = self.joint( jointSim.name() )
 			
 	 		# AMC describes object space transformations
 			#
 			mc.move( jointSim.sample("tx", jointSim.startFrame()),
					 jointSim.sample("ty", jointSim.startFrame()),
					 jointSim.sample("tz", jointSim.startFrame()),
					 mayaJoint.name, objectSpace=True, relative=True )
 			mc.xform( mayaJoint.name,
					  rotation=( jointSim.sample("rx", jointSim.startFrame()),
								 jointSim.sample("ry", jointSim.startFrame()),
								 jointSim.sample("rz", jointSim.startFrame())),
					  objectSpace=True, relative=True)
 		
 		self._bindPose = mc.dagPose(self.rootJoint.name, save=True, bindPose=True, name=(self.name() + "Bind"))

 	def _createSkinCluster( self, geometry ):
 		[ shape ] = mc.listRelatives(geometry.name(), type='shape', fullPath=True, allDescendents=True)
		
		deformers = [ self.joint(deformer).name for deformer in geometry.deformers() ]
					
		[cluster] = mc.deformer( geometry.name(), type="skinCluster" )
		
		# Assign the inclusive matrix of deformed geometry to the cluster.
		# worldMatrix[0] assumes the geometry is not instanced.
		#
		wm = mc.getAttr( "%s.worldMatrix[0]" % geometry.name() )
		setMatrixAttr( "%s.geomMatrix" % cluster, wm )
		
		for i in range(len(deformers)):
			if not mc.ls( "%s.lockInfluenceWeights" % deformers[i] ):
				mc.addAttr( deformers[i], longName="lockInfluenceWeights", shortName="liw", min=0, max=1, at="bool", defaultValue=0 )
			mc.connectAttr( "%s.lockInfluenceWeights" % deformers[i], "%s.lockWeights[%d]" % (cluster, i) )
			mc.connectAttr( "%s.worldMatrix[0]" % deformers[i], "%s.matrix[%d]" % (cluster, i) )
			# Assign the invlusive matrix inverse of the deformer
			# (i.e. joint) to the cluster.
			# worldInverseMatrix[0] assumes the joint is not instanced
			#
			wim = mc.getAttr( "%s.worldInverseMatrix[0]" % deformers[i] )
			setMatrixAttr( "%s.bindPreMatrix[%d]" % (cluster, i), wim )
		
		self.mayaScene.setClusterWeights( geometry, cluster )
		
	def bindSkin( self ):
		for geometry in self.geometryData:
			if not geometry:
				continue
			if not geometry.skin:
				continue
			if geometry.attached():
				# Attached geometry is parented to a joint instead of being
				# skinned.
				#
				continue
			if not geometry.weights() or not geometry.deformers():
				print >> sys.stderr, "Warning: %s has no skin weights and will not be bound." % geometry.name()
				continue
			
			if SceneDescription.eSkinType.smooth == self.sceneDesc().skinType:
				self._createSkinCluster( geometry )
			elif geometry.skin.bindChunks(self):
				mc.delete(geometry.name())		
		
	def build( self, mayaScene ):
		self.mayaScene = mayaScene

		if self.sceneDesc().loadSkeleton:
			self.buildSkeleton()
		
		if self.sceneDesc().loadGeometry:
			Timer.push("Build Geometry")
			self.buildGeometry()
			Timer.pop()
		
		# Make sure the agent scale doesn't also scale the translate values of
		# the sim data. We have to freeze the transform here since we won't
		# be allowed to after binding the skin
		#
		self.freezeAgentScale()
		
		if self.sceneDesc().loadPrimitives:
			Timer.push("Build Primitives")
			self.buildPrimitives()
			Timer.pop()
					
		if self.sceneDesc().loadSkin:
			Timer.push("Bind Skin")
			
			self.setBindPose()
			self.bindSkin()
			Timer.pop()
		
		if self.sceneDesc().loadSkeleton:
			# Has to happen after skin is bound
			self.scaleJoints()
			self._zeroPose = mc.dagPose(self.rootJoint.name, save=True, name=(self.name() + "Zero"))
			
		if self.sceneDesc().loadActions:
			self.buildCharacterSet()
			self.applyActions()
		
		if self._zeroPose:
			mc.dagPose( self._zeroPose, restore=True )
			
	def loadSim( self, animType ):
		'''Load the simulation data for this MayaAgent. It will either be
		   loaded as anim curves or through the msvSimLoader node.'''
		if SceneDescription.eAnimType.curves == animType:
			#==================================================================
			# Create Anim Curves
			#==================================================================
			sim = self.sim()
	
			for jointSim in sim.joints():
		 		mayaJoint = self.joint( jointSim.name() )
	
		 		for channelName in jointSim.channelNames():
		 			channelEnum = AgentDescription.channel2Enum[channelName]
		 			if mayaJoint.isChannelFree( channelEnum ):
						Timer.push("Setting Keyframe")
						times = range( jointSim.startFrame(),
									   jointSim.startFrame() + jointSim.numFrames(),
									   self.sceneDesc().frameStep )
		  				mc.setKeyframe( mayaJoint.name, attribute=channelName,
										inTangentType="linear", outTangentType="linear",
										time=times, value=0.0 )
		 				[ animCurve ] = mc.listConnections( "%s.%s" % (mayaJoint.name, channelName), source=True )
		 				
		 				offset = mayaJoint.channelOffsets[channelEnum]
		 				channels = [ offset + jointSim.sample(channelName, i) for i in times ]
		 				
		 				setMultiAttr( "%s.ktv" % animCurve, channels, "kv" )
		 				Timer.pop()
		else:
			#==================================================================
			# Create msvSimLoader Nodes
			#==================================================================
			simDir = self.mayaScene.sceneDesc.simDir()
			simType = self.mayaScene.sceneDesc.simType.strip('.')
			agentType = self._msvAgent.agentDesc.agentType
			instance = self._msvAgent.id
			
			simLoader = mc.createNode("msvSimLoader", name="msvSimLoader%d" % instance)
			mc.setAttr( "%s.simDir" % simLoader, simDir, type="string" )
			mc.setAttr( "%s.simType" % simLoader, simType, type="string" )
			mc.setAttr( "%s.agentType" % simLoader, agentType, type="string" )
			mc.setAttr( "%s.instance" % simLoader, instance )
			mc.connectAttr( "time1.outTime", "%s.time" % simLoader )
			
			i = 0
			for mayaJoint in self.joints.values():
				msvJoint = mayaJoint.msvJoint()
				mc.setAttr( "%s.joints[%d]" % (simLoader, i), msvJoint.name, type="string" )
				
				j = 0
				numTranslateChannels = 0
				# Use the joint's degrees-of-freedom and channel order to
				# determine which channels are present and which
				# transformations they correspond to
				for channel in msvJoint.order:
					if not msvJoint.dof[channel]:
						continue
 						
					if AgentDescription.isRotateEnum( channel ):
						src = "%s.output[%d].rotate[%d]" % (simLoader, i, (j-numTranslateChannels))
					else:
						src = "%s.output[%d].translate[%d]" % (simLoader, i, j)
						numTranslateChannels += 1
					dst = "%s.%s" % (mayaJoint.name, AgentDescription.enum2Channel[channel])
					mc.connectAttr( src, dst )
					j += 1
				
				i += 1
			

	def deleteSkeleton( self ):
		intermediateShapes = []
		attachedGeo = []
		for geo in self.geometryData:
			if not geo.skinnable():
				if geo.attached():
					attachedGeo.append(geo)
				continue
			history = mc.listHistory( geo.shapeName() )
			for node in history:
				if mc.objectType( node, isAType="shape" ):
					if mc.getAttr( "%s.intermediateObject" % node ):
						intermediateShapes.append( node )
		mc.delete( self.skelGroup )
		mc.delete( intermediateShapes )
		self.skelGroup = ""
		self.rootJoint = None
		self.joints = {}
		self.primitiveData = []
		# Attached geometry has been deleted with the skeleton
		#
		for geo in attachedGeo:
			self.geometryData.remove(geo)
   
