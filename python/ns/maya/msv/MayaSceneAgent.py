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

kAnimatableAttrs = ('rx', 'ry', 'rz', 'tx', 'ty', 'tz')

class MayaAction:
	def __init__(self, mayaAgent, action):
		self._action = action
		self._mayaAgent = mayaAgent
 	
 	def build( self ):
 		for channel in self._action.curves.keys():
 			curve = self._action.curves[channel]
 			tokens = channel.split()
 			if len(tokens) == 1:
 				object = self._mayaAgent.skelGroup
 				attr = tokens[0]
 			else:
  			 	object = self._mayaAgent.mayaJoint(tokens[0]).name
  			 	attr = tokens[1]

 			if not attr in kAnimatableAttrs:
 		 		# TODO: figure out how to handle non rot/trans attrs
 		 		continue
 		 	if object == self._mayaAgent.skelGroup:
 		 		# TODO: handle _agent animation... are these "agent curves"?
 		 		continue

 			baseValue = mc.getAttr("%s.%s" % (object, attr))
 			for key in curve.points:
 				mc.setKeyframe( object, attribute=attr,
								inTangentType="linear", outTangentType="linear",
								time=key[0] * self._action.maxPoints, value=key[1] + baseValue)
 			
 		clip = mc.clip(self._mayaAgent.characterSet,
					   startTime=0,
					   endTime=self._action.maxPoints,
					   allRelative=True,
					   scheduleClip=False)
 		mc.clip(self._mayaAgent.characterSet, name=clip, newName=self._action.name)
 

class MayaSceneAgent(MayaAgent.MayaAgent):
	def __init__(self, agent, mayaFactory, scene):
		MayaAgent.MayaAgent.__init__(self, agent, mayaFactory)
		self._scene = scene
		self.characterSet = ""
		self.actions = {}
			
 	def _buildCharacterSet(self):
 		setMembers = [ "%s.%s" % (mayaJoint.name, attr) for mayaJoint in self.mayaJoints.values() for attr in kAnimatableAttrs ]
 		self.characterSet = mc.character(setMembers, name=("%sCharacter" % self.name()))

	def _applyActions(self):
 		# The rotation order needed to build the skeleton does not apply
 		# to the animation - it is assumed to be xyz
 		#
 		for mayaJoint in self.mayaJoints.values():
 			mc.setAttr("%s.rotateOrder" % mayaJoint.name, MayaAgent.kRotateOrder2Enum['xyz'])

		for action in self.agentSpec().actions.values():
 	 		mc.dagPose(self._zeroPose, restore=True)
 	 		mayaAction = MayaAction( self, action )
 	 		self.actions[action.name] = mayaAction
 	 		print >> sys.stderr, "building action"
 	 		mayaAction.build()
 	 		
	def loadActions(self):
		self._buildCharacterSet()
		self._applyActions()
		
		if self._zeroPose:
			mc.dagPose( self._zeroPose, restore=True )
