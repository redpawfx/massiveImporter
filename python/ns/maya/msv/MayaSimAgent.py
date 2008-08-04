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

import ns.maya.msv.MayaAgent as MayaAgent
import ns.maya.msv.MayaUtil as MayaUtil

class eAnimType:
	curves, loader = range(2)

class MayaSimAgent(MayaAgent.MayaAgent):
	def __init__(self, agent, mayaFactory, sim):
		MayaAgent.MayaAgent.__init__(self, agent, mayaFactory)
		self._sim = sim
			
	def simData( self ):
		return self._agent.simData()
			
	def _loadSim(self, animType, frameStep):
		'''Load the simulation data for this MayaAgent. It will either be
		   loaded as anim curves or through the msvSimLoader node.'''
		if eAnimType.curves == animType:
			#==================================================================
			# Create Anim Curves
			#==================================================================
			simData = self.simData()
	
			for jointSim in simData.joints():
		 		mayaJoint = self.mayaJoint(jointSim.name())
	
		 		for channelName in jointSim.channelNames():
		 			channelEnum = AgentSpec.channel2Enum[channelName]
		 			if mayaJoint.isChannelFree( channelEnum ):
						times = range(jointSim.startFrame(),
									  jointSim.startFrame() + jointSim.numFrames(),
									  frameStep )
		  				mc.setKeyframe(mayaJoint.name, attribute=channelName,
									   inTangentType="linear", outTangentType="linear",
									   time=times, value=0.0 )
		  				channelAttr = "%s.%s" % (mayaJoint.name, channelName)
		 				[ animCurve ] = mc.listConnections(channelAttr,
														   source=True)
		 				
		 				offset = mayaJoint.channelOffsets[channelEnum]
		 				channels = [ offset + jointSim.sample(channelName, i) for i in times ]
		 				
		 				MayaUtil.setMultiAttr( "%s.ktv" % animCurve, channels, "kv" )
		else:
			#==================================================================
			# Create msvSimLoader Nodes
			#==================================================================
			simDir = self._sim.simDir
			simType = self._sim.simType.strip('.')
			agentType = self.agentSpec().agentType
			instance = self.id()
			
			simLoader = mc.createNode("msvSimLoader", name="msvSimLoader%d" % instance)
			mc.setAttr( "%s.simDir" % simLoader, simDir, type="string" )
			mc.setAttr( "%s.simType" % simLoader, simType, type="string" )
			mc.setAttr( "%s.agentType" % simLoader, agentType, type="string" )
			mc.setAttr( "%s.instance" % simLoader, instance )
			mc.connectAttr( "time1.outTime", "%s.time" % simLoader )
			
			i = 0
			for mayaJoint in self.mayaJoints.values():
				joint = mayaJoint.joint()
				mc.setAttr("%s.joints[%d]" % (simLoader, i), joint.name, type="string")
				
				j = 0
				numTranslateChannels = 0
				# Use the joint's degrees-of-freedom and channel order to
				# determine which channels are present and which
				# transformations they correspond to
				for channel in joint.order:
					if not joint.dof[channel]:
						continue
 						
 					src = ""
 					offset = ""
					if AgentSpec.isRotateEnum( channel ):
						src = "%s.output[%d].rotate[%d]" % (simLoader, i, (j-numTranslateChannels))
						offset = "%s.offsets[%d].rotateOffset[%d]" % (simLoader, i, (j-numTranslateChannels))
					else:
						src = "%s.output[%d].translate[%d]" % (simLoader, i, j)
						offset = "%s.offsets[%d].translateOffset[%d]" % (simLoader, i, j)
						numTranslateChannels += 1
					dst = "%s.%s" % (mayaJoint.name, AgentSpec.enum2Channel[channel])

					mc.setAttr( offset, mayaJoint.channelOffsets[channel] )
					mc.connectAttr( src, dst )
					j += 1
				
				i += 1
			

	def deleteSkeleton(self):
		intermediateShapes = []
		attachedGeo = []
		for geo in self.geometryData:
			if not geo.skinnable():
				if geo.attached():
					attachedGeo.append(geo)
				continue
			history = mc.listHistory(geo.shapeName())
			for node in history:
				if mc.objectType(node, isAType="shape"):
					if mc.getAttr("%s.intermediateObject" % node):
						intermediateShapes.append(node)
		mc.delete(self.skelGroup)
		mc.delete(intermediateShapes)
		self.skelGroup = ""
		self.rootJoint = None
		self.joints = {}
		self.primitiveData = []
		# Attached geometry has been deleted with the skeleton
		#
		for geo in attachedGeo:
			self.geometryData.remove(geo)
			
	def build(self, agentOptions, animType, frameStep):
		MayaAgent.MayaAgent.build(self, agentOptions)
		self._loadSim(animType, frameStep)
		self.setupDisplayLayers()

