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

import ns.bridge.data.AgentSpec as AgentSpec
import ns.bridge.data.Agent as Agent

def read(callsheet, sim):
	'''Load the simmed values of agent variables'''
 
 	if isinstance(callsheet, basestring):
		fileHandle = open(callsheet, "r")
	else:
		fileHandle = callsheet
 	
 	try:
 		try:
			for line in fileHandle:
				tokens = line.strip().split()
		 		if tokens:
		 			# 0   :	id
		 			# 1   :	name
		 			# 2-17:	placement matrix
		 			# 18  : keyword "cdl"
		 			# 19  : cdl file path
		 			# 20-?: variable names and values
		 			id = int(tokens[0])
		 			agentName = Agent.formatAgentName(tokens[1])
		 			agentSpec = sim.scene.agentSpec(sim.scene.resolvePath(tokens[19]))
		 					 			
			 		agent = sim.agent(agentName, id, agentSpec)
			 		
					if not agent:
						# Agent is not in one of the chosen "selections"
						#
						continue
					 			
		 			agent.placement = [ float(token) for token in tokens[2:18] ]
		 			for i in range(20, len(tokens), 2 ):
		 				agent.variableValues[tokens[i]] = float(tokens[i+1])
		finally:
			if fileHandle != callsheet:
		 		fileHandle.close()
	except:
 		print >> sys.stderr, "Error reading callsheet."
 		raise


        
