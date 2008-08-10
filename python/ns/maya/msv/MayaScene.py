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

import maya.mel
import maya.cmds as mc

import ns.bridge.data.Agent as Agent
import ns.bridge.data.AgentSpec as AgentSpec

import ns.maya.msv.MayaAgent as MayaAgent
import ns.maya.msv.MayaPlacement as MayaPlacement
import ns.maya.msv.MayaFactory as MayaFactory
import ns.maya.msv.MayaSceneAgent as MayaSceneAgent


class MayaScene:
	def __init__(self):
		self._factory = MayaFactory.MayaFactory()
	
	def build(self, scene, agentOptions):
		if scene.mas().terrainFile:
			self._factory.importObj(scene.mas().terrainFile, "terrain")
		
		MayaPlacement.build(self._factory, scene.mas())
		
		for agentSpec in scene.agentSpecs():
			agent = Agent.Agent(instanced=False)
			agent.agentSpec = agentSpec
			agent.name = agentSpec.agentType
			mayaAgent = MayaSceneAgent.MayaSceneAgent(agent, self._factory, scene)
			mayaAgent.build(agentOptions)
			self._factory.addAgent(mayaAgent)
		
		self._factory.cleanup()
		
		# The layers are off by default to speed up load, turn them on
		# now.
		#	
		MayaAgent.showLayers()

		