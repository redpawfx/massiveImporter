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

'''Read animation data from an AMC file.'''

import sys
import os.path

import ns.bridge.data.Agent as Agent
import ns.bridge.data.SimData as SimData

def read(amcFile, simData=None):
	'''Load animation data from a .amc file and adds it to an SimData.Agent.
	   The name of the SimData.Agent is gotten from the .amc file name.
	   If a simData is provided, it will be queried to get SimData.Agent.
	   If the specified SimData.Agent does not exist, the read will exit
	   early. If no simData is provided a new SimData.Agent is created.
	   In both cases the target SimData.Agent is returned (although if
	   a SimData was provided it will also store the target SimData.Agent).
	   For now amcFile must be a path to a .amc file (as opposed to an open
	   file handle).'''
 
 	# AMC sim files are named: agentType.#.amc where agentType.# is
	# the name of that particular agent instance
	#
	tokens = os.path.basename(amcFile).split(".")
	agentName = Agent.formatAgentName(tokens[0], tokens[1])
	
 	# Python 2.4 limitation: try... except: finally: doesn't work,
 	# have to nest try... except: in try... finally:
	try:
		if simData:
			agentSim = simData.agent(agentName)
			if not agentSim:
				# Agent is not in one of the chosen "selections"
				#
				return None
		else:
			agentSim = SimData.Agent(agentName)
		
		path = os.path.dirname(amcFile)
		
		fileHandle = open(amcFile, "r")
		try:
			frame = 0
			for line in fileHandle:
				tokens = line.strip().split()
				if tokens:
					if tokens[0][0] == ":":
						# file options
						continue
					elif len(tokens) == 1:
						# sample number
						frame = int(tokens[0])
					else:
						jointName = tokens[0]
 					
	 					data = []
	 					for i in range(1, len(tokens)):
	 						data.append(float(tokens[i]))
	 					
	 					agentSim.addSample(jointName, frame, data) 
	 	finally:
			fileHandle.close()				
	except:
		print >> sys.stderr, "Error reading AMC file: %s" % amcFile
		raise
	
	return agentSim




        
