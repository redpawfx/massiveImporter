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
import os
import unittest
import difflib
import filecmp

import ns.bridge.io.CDLReader as CDLReader
import ns.bridge.io.CDLWriter as CDLWriter

class TestIO(unittest.TestCase):
	
	def setUp(self):
		self.scratchFile = "R:/scratch/out.cdl"
		
	def tearDown(self):
		try:
			os.remove(self.scratchFile)
		except:
			pass

	def testFuzzy(self):
		'''	Read the fuzzy nodes from a test file, write them out again, and
			compare the two files. They should be identical except for a
			comment at the beginning of the files. '''
		input = "R:/massive/testdata/cdl/man/CDL/fuzzy_nodes.cdl"
	
		agentSpec = CDLReader.read(input, ["fuzzy"])
		
		nodes = agentSpec.brain.nodes()
		self.assertEqual(30, len(nodes))

		fileHandle = open(self.scratchFile, "w")
		CDLWriter.write(fileHandle, agentSpec)
		fileHandle.close()
	
		inputHandle = open(input, "r")
		scratchHandle = open(self.scratchFile, "r")
		inputLines = inputHandle.readlines()[1:]
		scratchLines = scratchHandle.readlines()[1:]
		inputHandle.close()
		scratchHandle.close()
		self.assertEqual(inputLines, scratchLines)
		#os.system("xdiff.exe %s %s" % (input, self.scratchFile))

if __name__ == '__main__':
	try:
		unittest.main()
	finally:
		sys.exit()

	
