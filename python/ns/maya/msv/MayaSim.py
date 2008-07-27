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

import ns.maya.msv.MayaFactory as MayaFactory
import ns.maya.msv.MayaAgent as MayaAgent
import ns.maya.msv.MayaSimAgent as MayaSimAgent

class MayaSim:
	def __init__(self):
		self._factory = MayaFactory.MayaFactory()
	
	def build(self, sim, animType, frameStep, cacheGeometry, cacheDir,
			  deleteSkeleton, agentOptions):
		if sim.scene.mas().terrainFile:
			self._factory.importObj(sim.scene.mas().terrainFile, "terrain")
			
		mayaAgents = []
		startFrame = -sys.maxint
		endFrame = -sys.maxint
		
		for agent in sim.agents():
			mayaAgent = MayaSimAgent.MayaSimAgent(agent, self._factory, sim)
			mayaAgent.build(agentOptions)
			mayaAgent.loadSim(animType, frameStep)
			
			# Presumably every agent will be simmed over the same frame
			# range - however since the frame ranges could conceivably
			# be different, find and and store the earliest startFrame
			# and latest endFrame
			#
			if mayaAgent.simData():
				if -sys.maxint == startFrame or mayaAgent.simData().startFrame < startFrame:
					startFrame = mayaAgent.simData().startFrame
				if -sys.maxint == endFrame or mayaAgent.simData().endFrame > endFrame:
					endFrame = mayaAgent.simData().endFrame
			
			mayaAgent.setupDisplayLayers()
			mayaAgents.append(mayaAgent)

		if cacheGeometry:
			# Create geometry caches for each agent.
			#
			meshes = []
			for mayaAgent in mayaAgents:
				meshes.extend( [ geometry.shapeName() for geometry in mayaAgent.geometryData ] )
			cacheFileName = "%s_%s" % (sim.scene.baseName(), sim.range)
			
			mc.cacheFile( directory=cacheDir,
						  singleCache=True,
						  doubleToFloat=True,
						  format="OneFilePerFrame",
						  simulationRate=1,
						  sampleMultiplier=1,
						  fileName=cacheFileName,
						  startTime=startFrame,
						  endTime=endFrame,
						  points=meshes )
			
			# There's a bug in maya where cacheFile will sometimes write a
			# partial path into the cache instead of the full path. To makes
			# sure the attachFile works, we have to query the actual channel
			# names
			cacheFileFullName = "%s/%s.xml" % (cacheDir, cacheFileName)
			meshes = mc.cacheFile(query=True, fileName=cacheFileFullName, channelName=True)
			
			switches = [ maya.mel.eval( 'createHistorySwitch( "%s", false )' % mesh ) for mesh in meshes ]
			switchAttrs = [ ( "%s.inp[0]" % switch ) for switch in switches ]
			mc.cacheFile(attachFile=True,
						 fileName=cacheFileName,
						 directory=cacheDir,
						 channelName=meshes,
						 inAttr=switchAttrs)
			for switch in switches:
				mc.setAttr("%s.playFromCache" % switch, True)
	
			if deleteSkeleton:
				# After creating a geometry cache the skeleton, anim curves, and
				# skin clusters are no longer needed to playback the sim. To save
				# memory the user can choose to delete them.
				#
				for mayaAgent in mayaAgents:
					mayaAgent.deleteSkeleton()

		self._factory.cleanup()
		
		# The layers are off by default to speed up load, turn them on
		# now.
		#	
		MayaAgent.showLayers()
