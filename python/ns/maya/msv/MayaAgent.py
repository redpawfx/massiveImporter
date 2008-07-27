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

import ns.bridge.data.AgentSpec as AgentSpec
import ns.bridge.data.Agent as Agent
import ns.maya.msv.MayaSkin as MayaSkin
import ns.maya.msv.MayaUtil as MayaUtil

_animatable = ('rx', 'ry', 'rz', 'tx', 'ty', 'tz')
_rotateOrder2Enum = dict([['xyz', 0], ['yzx', 1], ['zxy', 2], ['xzy', 3], ['yxz', 4], ['zyx', 5]])	
_masterSegments = {}


class Options:
	def __init__(self):
		self.loadGeometry = True
		self.loadPrimitives = False
		self.loadMaterials = True
		self.skinType = MayaSkin.eSkinType.smooth
		self.instancePrimitives = True
		self.materialType = "blinn"

class MayaMaterial:
	def __init__(self,
				 agent,
				 mayaFactory,
				 material,
				 materialType):
		self._agent = agent
		self._factory = mayaFactory
		self._material = material
		self.materialType = materialType
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
			color = MayaUtil.hsvToRgb( color )
		return color
		
	def id(self):
		return self._material.id
	
	def name(self):
		if self.colorMap != self._material.rawColorMap:
			basename = os.path.basename(self.colorMap)
			return os.path.splitext(basename)[0]
		elif self._material.name:
			return self._material.name
		else:
			return "%s%d" % (self._materialType, self.id())
		
	def build(self):
		self.colorMap = self._agent.replaceEmbeddedVariables( self.colorMap )
		
		self.specular = self._resolveColor( self._material.specular,
											self._material.specularVar,
											self._material.specularSpace )
		self.ambient = self._resolveColor( self._material.ambient,
											self._material.ambientVar,
											self._material.ambientSpace )
		# The V component Massive diffuse HSV color is represented as the
		# single 'diffuse' attribute in Maya.
		#
		diffuse = self._resolveColor( self._material.diffuse,
									  self._material.diffuseVar,
									  self._material.diffuseSpace )
		diffuse = MayaUtil.rgbToHsv( diffuse )
		self.diffuse = diffuse[2]
		
		if self._material.roughnessVar:
			# For now only the color map is allowed to vary. If a variable is
			# present elsewhere its default value will be used
			#
			self.roughness = self._agent.variableValue( self._material.roughnessVar,
														asInt=False,
														varies=False )
		else:
			self.roughness = self._material.roughness
		
		#print "map: %s" % `self.colorMap`
		#print "specular: %s" % `self.specular`
		#print "ambient: %s" % `self.ambient`
		#print "diffuse: %s" % `self.diffuse`
		
		self.sgName = self._factory.buildMaterial(self)		

class MayaGeometry:
	def __init__(self, mayaAgent, geometry):
		self.mayaAgent = mayaAgent
		self.geometry = geometry
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
		return bool(self.geometry.attach)
	
	def skinnable( self ):
		return not self.attached() and self.weights()
	
	def deformers( self ):
		return self.geometry.deformers()

	def weights( self ):
		return self.geometry.weights()
	
	def file( self ):
		return self.geometry.file
	
	def build(self, skinType, loadMaterials, materialType):
		if not self.geometry.file:
			# it is perfectly legal to have non-geometry:
			# a geometry node with no obj file. Massive just
			# doesn't display anything
			return

		# mo=0 makes causes multiple objects to be combined into one mesh
		# TODO: returnNewNodes is a relatively new flag (8.0? 8.5?) need something
		#		if this is to work with 7.0
		# TODO: maybe use namespaces? Or a better renaming prefix?
		if self.mayaAgent:
			self.mayaAgent.importGeometry(self, self.geometry.name, skinType)
			if self.attached():
				[name] = mc.parent(self.name(),
								   self.mayaAgent.mayaJoint(self.geometry.attach).name )
				[name] = mc.ls( name, long=True )
				self.setName( name )
			if loadMaterials:
				material = self.mayaAgent.material(self.geometry.material, materialType)
				mc.sets(self.name(),
						edit=True,
						forceElement=material.sgName)
			elif MayaSkin.eSkinType.instance == skinType:
				# When using chunk skinning with instances the newly
				# instanced chunks won't have any shading connections,
				# assign some now
				#
				mc.sets( self.name(), edit=True, forceElement="initialShadingGroup" )
			self.mayaAgent.registerGeometry(self, skinType)

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
  			 	object = self._agent.mayaJoint(tokens[0]).name
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
		self.baseName = (mayaJoint.joint().name + "Segment")
		self.name = ""
		
	def create( cls, msvPrimitive, mayaJoint ):
		if isinstance( msvPrimitive, AgentSpec.Tube ):
			return MayaTube( msvPrimitive, mayaJoint )
		elif isinstance( msvPrimitive, AgentSpec.Sphere ):
			return MayaSphere( msvPrimitive, mayaJoint )
		elif isinstance( msvPrimitive, AgentSpec.Box ):
			return MayaBox( msvPrimitive, mayaJoint )
		elif isinstance( msvPrimitive, AgentSpec.Disc ):
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
 	def __init__(self, agent, joint, factory):
 		self.agent = agent
 		self._joint = joint
 		self._factory = factory
 		self.primitive = None
 		self.name = ""
 		self.channelOffsets = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]

 	def joint( self ):
 		return self._joint
 	
 	def primitiveName( self ):
 		if self.primitive:
 			return "%s|%s" % (self.name, self.primitive.name)
 		else:
 			return ""

 	def isChannelFree( self, channel ):
 		return self._joint.dof[channel]

 	def rotateOrderString( self, reversed ):
 		order = self._joint.order
 		rotateOrder = ""
 		indices = []
 		if reversed:
 			indices = range(len(order) - 1, -1, -1)
 		else:
 			indices = range(len(order))
 		for i in indices:
 			if AgentSpec.kRX == order[i]:
 				rotateOrder += "x"
 			elif AgentSpec.kRY == order[i]:
 				rotateOrder += "y"
 			elif AgentSpec.kRZ == order[i]:
 				rotateOrder += "z"
 		return rotateOrder

 	def scale(self):
		if self._joint.scaleVar:
			val = self.agent.variableValue(self._joint.scaleVar, False)
			mc.scale( val, val, val, self.name )
			
	def setChannelOffsets(self):
		'''Treat the current translate values as the base translation. Any
		   translate animation applied will be relative to these values.'''
		[baseTranslate] = mc.getAttr("%s.translate" % self.name)
		self.channelOffsets[AgentSpec.channel2Enum["tx"]] = baseTranslate[0]
 		self.channelOffsets[AgentSpec.channel2Enum["ty"]] = baseTranslate[1]
 		self.channelOffsets[AgentSpec.channel2Enum["tz"]] = baseTranslate[2]
 	 	
 	def build(self):
 		self.name = mc.createNode("joint", name=self._joint.name)
 
  		mc.setAttr((self.name + ".rotateOrder"), _rotateOrder2Enum[self.rotateOrderString(False)])
 
 		if self._joint.translate:
			mc.move( self._joint.translate[0], self._joint.translate[1], self._joint.translate[2],
					 self.name, objectSpace=True, relative=True )
		
		if self._joint.transform:
			mc.xform( self.name, matrix=self._joint.transform, objectSpace=True, relative=True)
			
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
 	
 		if self._joint.parent:
 			[self.name] = mc.parent(self.name, self.agent.mayaJoint(self._joint.parent).name, relative=True)
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
			
	def buildPrimitive(self, instance):
		self.primitive = MayaPrimitive.create( self._joint.primitive, self )
		self._factory.buildPrimitive(self.primitive, instance)

		# Primitives are created after freezing transforms on the agent group
		# To make sure they are also scaled up by the agent heigh, manually
		# scale them here. For skinning reasons, the individual joint scales
		# are applied later, so we don't have to account for them here.
		#
		if self.agent.agentSpec().scaleVar:
			val = self.agent.variableValue( self.agent.agentSpec().scaleVar, False )
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
	def __init__(self, agent, mayaFactory):
		self.reset()
		self._agent = agent
		self._factory = mayaFactory
	
	def reset(self):
		self._factory = None
		self._agent = None
		self._agentGroup = ""
		self.skelGroup = ""
		self.rootJoint = None
		self.geometryData = []
		self.materialData = []
		self.primitiveData = []
		self._zeroPose = ""
		self._bindPose = ""
		self.characterSet = ""

		self.mayaJoints = {}
		self.actions = {}

	def name( self ):
		return self._agent.name
	
	def agentSpec( self ):
		return self._agent.agentSpec
	
	def agentType( self ):
		return self.agentSpec().agentType
	
	def id(self):
		return self._agent.id

	def variableValue( self, variableName, asInt=False, varies=True ):
		return self._agent.variableValue( variableName, asInt, varies )

	def replaceEmbeddedVariables( self, s ):
		return self._agent.replaceEmbeddedVariables( s )

	def importGeometry(self, mayaGeometry, groupName, skinType):
		return self._factory.importGeometry(mayaGeometry, groupName, skinType)

	def mayaJoint( self, mayaJointName ):
		return self.mayaJoints[ mayaJointName ]
	
	def material(self, id, materialType):
		'''Return the MayaMaterial with the given ID. Create the MayaMaterial
		   from the Massive Material if needed. This guarantees that we only
		   create materials for geometry that is actually used.'''
		if id >= len(self.materialData):
			self.materialData.extend( [None] * ((id + 1) - len(self.materialData)) )
		if not self.materialData[id]:
			mayaMaterial = MayaMaterial(self,
										self._factory,
										self.agentSpec().materialData[id],
										materialType)
			self.materialData[id] = mayaMaterial
			mayaMaterial.build()

		return self.materialData[id]
	
	def agentGroup( self ):
		if not self._agentGroup:
			self._agentGroup = mc.group(empty=True, name=self.name())
			if self.agentSpec().scaleVar:
				val = self.variableValue(self.agentSpec().scaleVar, False)
				mc.scale(val, val, val, self._agentGroup)
			self._agentGroup = '|%s' % self._agentGroup
		return self._agentGroup

	def registerPrimitive( self, primitive ):
		self.primitiveData.append(primitive)
	
	def registerGeometry(self, mayaGeometry, skinType):
		self.geometryData.append(mayaGeometry)
		# if the geometry is attached it will already be parented to a
		# joint. And if we are chunk skinning using instances the geometry
		# should stay under the master group.
		#
		if (not mayaGeometry.attached() and
			MayaSkin.eSkinType.instance != skinType):
			[name] = mc.parent(mayaGeometry.name(), self.agentGroup(), relative=True)
 			[name] = mc.ls(name, long=True)
 			mayaGeometry.setName(name)
 	
	def registerRootJoint( self, rootJoint ):
		assert not self.skelGroup
		self.rootJoint = rootJoint
		self.skelGroup = mc.group(self.rootJoint.name, name=self.name(), parent=self.agentGroup(), relative=True)
		self.skelGroup = "%s|%s" % (self.agentGroup(), self.skelGroup)
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

	def _applyActions(self):
 		# The rotation order needed to build the skeleton does not apply
 		# to the animation - it is assumed to be xyz
 		#
 		for mayaJoint in self.mayaJoints.values():
 			mc.setAttr("%s.rotateOrder" % mayaJoint.name, _rotateOrder2Enum['xyz'])

		for msvAction in self.agentSpec().actions.values():
 	 		mc.dagPose(self._zeroPose, restore=True)
 	 		mayaAction = MayaAction( self, msvAction )
 	 		self.actions[msvAction.name] = mayaAction
 	 		mayaAction.build()

 	def _scaleJoints(self):
 		for mayaJoint in self.mayaJoints.values():
 			mayaJoint.scale()
 			
  	def _freezeAgentScale(self):
  		'''Make sure the agent scale doesn't also scale the translate values of
		   the sim data. We have to freeze the transform here since we won't
		   be allowed to after binding the skin'''
	
	  	# Freezing the root node's transform may update the translate values
	  	# of any/all mayaJoints in the skeleton, store those new translations as
	  	# the base values.
	  	#
  		mc.makeIdentity(self.agentGroup(), apply=True,
						translate=True, rotate=True, scale=True,
						normal=0)
 		for mayaJoint in self.mayaJoints.values():
 			mayaJoint.setChannelOffsets()

 	def _buildCharacterSet(self):
 		setMembers = [ "%s.%s" % (mayaJoint.name, attr) for mayaJoint in self.mayaJoints.values() for attr in _animatable ]
 		self.characterSet = mc.character(setMembers, name=("%sCharacter" % self.name()))
 
	def _buildSkeleton(self):
		for joint in self.agentSpec().jointData:
			if not joint:
				# some ids may not be used (e.g. 0)
				continue
			
			mayaJoint = MayaJoint(self, joint, self._factory)
			self.mayaJoints[joint.name] = mayaJoint
			mayaJoint.build()
			
	def _buildPrimitives(self, instance):
		for mayaJoint in self.mayaJoints.values():
			mayaJoint.buildPrimitive(instance)
					
	def _buildGeometry(self, skinType, loadMaterials, materialType):
		for geometry in AgentSpec.GeoIter( self.agentSpec().geoDB, self ):
			if not geometry:
				# some ids may not be used (e.g. 0)
				continue
			mayaGeometry = MayaGeometry(self, geometry)
			mayaGeometry.build(skinType, loadMaterials, materialType)
 
  	def _setBindPose( self ):
 		# The bind pose is stored in frame 1
 		if not self.agentSpec().bindPoseData:
 			return
 	
 		for jointSim in self.agentSpec().bindPoseData.joints():
 			mayaJoint = self.mayaJoint(jointSim.name())
 			
 	 		# AMC describes object space transformations
 			#
 			mc.move(jointSim.sample("tx", jointSim.startFrame()),
					jointSim.sample("ty", jointSim.startFrame()),
					jointSim.sample("tz", jointSim.startFrame()),
					mayaJoint.name, objectSpace=True, relative=True )
 			mc.xform(mayaJoint.name,
					 rotation=(jointSim.sample("rx", jointSim.startFrame()),
							   jointSim.sample("ry", jointSim.startFrame()),
							   jointSim.sample("rz", jointSim.startFrame())),
					 objectSpace=True, relative=True)
 		
 		self._bindPose = mc.dagPose(self.rootJoint.name, save=True, bindPose=True, name=(self.name() + "Bind"))

 	def _createSkinCluster(self, geometry):
 		[ shape ] = mc.listRelatives(geometry.name(), type='shape', fullPath=True, allDescendents=True)
		
		deformers = [ self.mayaJoint(deformer).name for deformer in geometry.deformers() ]
					
		[cluster] = mc.deformer( geometry.name(), type="skinCluster" )
		
		# Assign the inclusive matrix of deformed geometry to the cluster.
		# worldMatrix[0] assumes the geometry is not instanced.
		#
		wm = mc.getAttr( "%s.worldMatrix[0]" % geometry.name() )
		MayaUtil.setMatrixAttr( "%s.geomMatrix" % cluster, wm )
		
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
			MayaUtil.setMatrixAttr( "%s.bindPreMatrix[%d]" % (cluster, i), wim )
		
		self._factory.setClusterWeights( geometry, cluster )
		
	def _bindSkin(self, skinType):
		for mayaGeometry in self.geometryData:
			if not mayaGeometry:
				continue
			if not mayaGeometry.skin:
				continue
			if mayaGeometry.attached():
				# Attached geometry is parented to a joint instead of being
				# skinned.
				#
				continue
			if not mayaGeometry.weights() or not mayaGeometry.deformers():
				print >> sys.stderr, "Warning: %s has no skin weights and will not be bound." % geometry.name()
				continue
			
			if MayaSkin.eSkinType.smooth == skinType:
				self._createSkinCluster(mayaGeometry)
			elif mayaGeometry.skin.bindChunks(self):
				mc.delete(mayaGeometry.name())		
		
	def build(self, options):
		self._buildSkeleton()
		
		if options.loadGeometry:
			self._buildGeometry(options.skinType,
								options.loadMaterials,
								options.materialType)
		
		# Make sure the agent scale doesn't also scale the translate values of
		# the sim data. We have to freeze the transform here since we won't
		# be allowed to after binding the skin
		#
		self._freezeAgentScale()
		
		if options.loadPrimitives:
			self._buildPrimitives(options.instancePrimitives)
					
		if options.loadGeometry:
			self._setBindPose()
			self._bindSkin(options.skinType)
		
		# Has to happen after skin is bound
		self._scaleJoints()
		self._zeroPose = mc.dagPose(self.rootJoint.name, save=True, name=(self.name() + "Zero"))
			
		#if self.simManager().loadActions:
		#	self.buildCharacterSet()
		#	self.applyActions()
		#
		#if self._zeroPose:
		#	mc.dagPose( self._zeroPose, restore=True )
			

