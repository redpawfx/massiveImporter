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

import ns.bridge.data.AgentSpec as AgentSpec

def _writePlace(fileHandle, mas):
	'''Write a Place block.'''
 	if not mas.groups and not mas.locators:
 		# For now we only care about groups and locators
 		return
 	
 	fileHandle.write("Place\n")
 	
 	for group in mas.groups:
 		fileHandle.write("\tgroup %d %s\n" % (group.id, group.name))
 		# MasReader expeccts every group block to have 3 lines, but, for
 		# now we don't write any of that info out
 		fileHandle.write("\t\ttranslate\n")
 		fileHandle.write("\t\tcolour\n")
 		fileHandle.write("\t\tcdl\n")
 		fileHandle.write("\n")
 	
 	for locator in mas.locators:
 		# locked locators store more than just group id and position, but, for
 		# now that's all we read or write
 		fileHandle.write("\tlock %d [%f %f %f]\n" % ( locator.group,
													  locator.position[0],
													  locator.position[1], 
													  locator.position[2]))

 	fileHandle.write("End place\n")

def write(fileHandle, agentSpec):
	'''Write Massive agent information in .cdl format.'''
	
	# TODO: define a global version number an use that
	fileHandle.write("# CDL created with MsvTools for Maya version 1.0.0\n\n")
	
	for token in agentSpec.cdlStructure:
		if (token == "object"):
			fileHandle.write("object %s\n" % agentSpec.agentType)
		elif (token == "variable"):
			for var in agentSpec.variables.values():
				fileHandle.write("        variables %s %.6f [%.6f %.6f] %s\n" % (var.name, var.default, var.min, var.max, var.expression))
		elif (token == "scale_var"):
			fileHandle.write("scale_var %s\n" % agentSpec.scaleVar)
		elif (token == "bind_pose"):
			fileHandle.write("bind_pose %s\n" % agentSpec.bindPoseFile)
		else:
			try:
				fileHandle.write("%s" % agentSpec.leftovers[token])
			except:
				pass	



        
