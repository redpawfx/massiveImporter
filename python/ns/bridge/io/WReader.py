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

# Node definition
class WReader:
	def __init__(self):
		self._fullName = ""
		self._path = ""
		self._maxInfluences = 0
		self.deformers = []
		self.weights = []
		
 	def read( self, fullName ):
 		'''Load skin weights from a Massive .w (weights) file'''
 		
 		try:
 			if not os.path.isfile(fullName):
 				return
 			
	 		self._fullName = fullName
	 		self._path = os.path.dirname( fullName )

		 	fileHandle = open(self._fullName, "r")

			deformers = []
			tokens = []
			weights = []
			maxInfluences = 0
			
			for line in fileHandle:
				tokens = line.strip().split()
				if tokens:
					if tokens[0][0] == "#":
						# Comment
						continue
					elif tokens[0] == "deformer":
						id = int(tokens[1])
				 		numDeformers = len(self.deformers)
				 		if id >= numDeformers:
				 			self.deformers.extend([ "" ] * (id - numDeformers + 1))
				 		
				 		self.deformers[id] = tokens[2]
					else:
						# TODO: see if storing 0s for joints that have
						# no influence is a problem. Storing the influences
						# sparsely may make applying the weights later more
						# complex
						#
						numTokens = len(tokens)
						vtx = int(tokens[0][:-1])
						influences = [0] * len(self.deformers)
						count = 0
						for i in range(1, numTokens, 2):
							influences[int(tokens[i])] = float(tokens[i+1])
							count += 1
						# keep track of the maximum number of influences on a
						# given vertex so we can use it to optimize the skin
						# deformers later
						#
						if count > self._maxInfluences:
							self._maxInfluences = count
						self.weights.append(influences)
	
			fileHandle.close()
		 		
	 	except:
	 		print >> sys.stderr, "Error reading Weights file: %s" % self._fullName	
	 		raise


        
