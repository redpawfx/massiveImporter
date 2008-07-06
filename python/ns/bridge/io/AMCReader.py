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

import ns.bridge.data.Sim as Sim
import ns.bridge.data.AgentDescription as AgentDescription

class AMCReader:
	def __init__(self, fullName):
		self.fullName = fullName
		# AMC sim files are named: agentType.#.amc where agentType.# is
		# the name of that particular agent instance
		#
		tokens = os.path.basename( fullName ).split(".")
		self.agentName = AgentDescription.formatAgentName( tokens[0], tokens[1] )

	def read(self, sim):
		'''Load animation data from an AMC file, Returns a Sim object that
		   stores some number of frames of animation data for a single agent'''
	 
	 	# Python 2.4 limitation: try... except: finally: doesn't work,
	 	# have to nest try... except: in try... finally:
		try:
			agent = sim.agent( self.agentName )
			if not agent:
				# Agent is not in one of the chosen "selections"
				#
				return
			
			path = os.path.dirname( self.fullName )
			
			try:
				fileHandle = open(self.fullName, "r")
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
		 					
		 					agent.addSample( jointName, frame, data ) 
		 	finally:
				fileHandle.close()				
		except:
			print >> sys.stderr, "Error reading AMC file: %s" % self.fullName	
			raise




        
