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
import os.path

import ns.py.Timer as Timer
import ns.maya.Progress as Progress

import ns.maya.msv.AMCReader as AMCReader
import ns.maya.msv.APFReader as APFReader
import ns.maya.msv.AgentDescription as AgentDescription

class _ApfFile:
	def __init__(self, file):
		# APF sim files are named: frame.#.apf where # is the current
		# frame
		#
		tokens = os.path.basename( file ).split(".")
		self.frame = int(tokens[1])
		self.file = file

	def cmp(a, b):
		return a.frame - b.frame
	cmp = staticmethod(cmp)
		

def _readAPFSim( simFiles, sceneDesc, progressRange ):
	# Sort the files first to guarantee that samples are added to the sim
	# in sequential order. Otherwise it becomes awkward to manage the channel
	# data if the sim doesn't always start at frame 1
	#
	apfFiles = []
	for simFile in simFiles:
		apfFiles.append( _ApfFile( simFile ) )
	
	apfFiles.sort( _ApfFile.cmp )

	progressIncrement = int(progressRange / len(apfFiles))	
	for apfFile in apfFiles:
		Timer.push("Read APF")
		Progress.setProgressStatus(os.path.basename(apfFile.file))
		APFReader.read( apfFile.file, sceneDesc, apfFile.frame )
		Progress.advanceProgress( progressIncrement )
		Timer.pop()

def _readAMCSim( simFiles, sceneDesc, progressRange ):
	progressIncrement = int(progressRange / len(simFiles))	
	for simFile in simFiles:
		Progress.setProgressStatus(os.path.basename(simFile))
		# AMC sim files are named: agentType.#.amc where agentType.# is
		# the name of that particular agent instance
		#
		tokens = os.path.basename( simFile ).split(".")
		agentName = AgentDescription.formatAgentName( tokens[0], tokens[1] )
		agentId = int(tokens[1])
		try:
			agent = sceneDesc.buildAgent( agentName, agentId )
		except:
			print >> sys.stderr, "Warning: No CDL file provided for agent %s. Skipping." % agentName
			continue	
		
		if not agent:
			# Agent is not in one of the chosen "selections"
			#
			continue

		Timer.push("Read AMC")
		agent.sim = AMCReader.read( simFile, agent.agentDesc )
		Timer.pop()
		Progress.advanceProgress( progressIncrement )

def read(dirPath, simType, sceneDesc, progressRange):
	'''Load sim files from a sim directory'''
	
	try:
		simFiles = [ "%s%s" % (dirPath, file) for file in os.listdir(dirPath) if os.path.splitext(file)[1] == simType ]
		
		if ".amc" == simType:
			return _readAMCSim( simFiles, sceneDesc, progressRange )
		elif ".apf" == simType:
			return _readAPFSim( simFiles, sceneDesc, progressRange )
		else:
			raise "Unknown sim type: %s" % simType
	 		
 	except:
 		print >> sys.stderr, "Error reading simulation: %s" % dirPath	
 		raise

        
