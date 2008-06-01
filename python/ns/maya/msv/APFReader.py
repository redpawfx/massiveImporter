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

'''Read animation data from an APF file.'''

import sys
import os.path

import ns.maya.msv.Sim as Sim

class APFReader:
	def __init__(self, fullName):
		'''Initialize the APF reader by parsing the file name. APF sim files
		   are named: frame.#.apf where # is the current frame'''
		tokens = os.path.basename( fullName ).split(".")
		self.frame = int(tokens[1])
		self.fullName = fullName

	def read(self, sim):
		'''Load animation data from an APF file. Adds a single frame's
		   worth of animation data to each agent'''
	 
	 	# Python 2.4 limitation: try... except: finally: doesn't work,
	 	# have to nest try... except: in try... finally:
		try:
			try:
		 		path = os.path.dirname( self.fullName )
		 		fileHandle = open(self.fullName, "r")
		 		agent = None
		 		
		 		for line in fileHandle:
		 			tokens = line.strip().split()
		 			if tokens:
		 				if tokens[0] == "BEGIN":
		 					agent = sim.agent( tokens[1] )
		 					if not agent:
								# Agent is not in one of the chosen "selections"
								#
								continue
		 				elif agent:
		 					jointName = tokens[0]
		 					
		 					data = []
		 					for i in range(1, len(tokens)):
		 						data.append(float(tokens[i]))
		 					
		 					agent.addSample( jointName, self.frame, data ) 
			except:
				print >> sys.stderr, "Error reading APF file: %s" % self.fullName	
				raise
		finally:
			fileHandle.close()
	 	
	def cmp(a, b):
		'''Comparison method used to sort APF files in order of increasing
		   frame number.'''
		return a.frame - b.frame
	cmp = staticmethod(cmp)
	
	        
