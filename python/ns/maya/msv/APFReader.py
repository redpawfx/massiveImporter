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

import ns.maya.msv.AgentDescription as AgentDescription

def read(fullName, sceneDesc, frame):
	'''Load animation data from an APF file. Adds a single frame's
	   worth of animation data to each agent'''
 
 	try:
 		path = os.path.dirname( fullName )
 		
 		fileHandle = open(fullName, "r")
 		
 		agent = None
 		
 		for line in fileHandle:
 			tokens = line.strip().split()
 			if tokens:
 				if tokens[0] == "BEGIN":
 					agent = sceneDesc.buildAgent( tokens[1] )
 					
 					if not agent:
						# Agent is not in one of the chosen "selections"
						#
						continue
 					
 					if not agent.sim:
 						agent.sim = AgentDescription.Sim()
 				elif agent:
 					jointName = tokens[0]
 					try:
 						joint = agent.msvJoint( jointName )
 					except:
 						continue
 					
 					dof = joint.dof
 					order = joint.order
 					
					rotate = [ 0.0, 0.0, 0.0 ]
 					translate = [ 0.0, 0.0, 0.0 ]
 						 					
 					i = 1
 					# Determine degrees of freedom and use them to figure out
 					# which tokens correspond to which channels
 					#
 					for channel in order:
 						if not dof[channel]:
 							continue
 						
 						if AgentDescription.kRX == channel:
 							rotate[0] = float(tokens[i])
 						elif AgentDescription.kRY == channel:
 							rotate[1] = float(tokens[i])
 						elif AgentDescription.kRZ == channel:
 							rotate[2] = float(tokens[i])
 						elif AgentDescription.kTX == channel:
 							translate[0] = float(tokens[i])
 						elif AgentDescription.kTY == channel:
 							translate[1] = float(tokens[i])
 						elif AgentDescription.kTZ == channel:
 							translate[2] = float(tokens[i])
 						i += 1
 					
 					agent.sim.addSample( frame, jointName, rotate, translate )
	 		
	 	fileHandle.close()
	 		
 	except:
 		print >> sys.stderr, "Error reading APF file: %s" % fullName	
 		raise

        
