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

import ns.bridge.io.CDLReader as CDLReader
import ns.evolve.Genotype as Genotype
import ns.tests.TestUtil as TestUtil


class TestMutateInput(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/input.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No Input parameters should mutate.'''
		self.geno.rand.default.floatDefault = 0.1
		self.geno.getNode("input").mutateParameters()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.assertEqual("", self.agentSpec.brain.getNode("input").channel)
		self.assertEqual("position", self.agentSpec.brain.getNode("input").integrate)
		self.assertEqual([0.0, 1.0], self.agentSpec.brain.getNode("input").range)
		self.assertAlmostEqual(0.0, self.agentSpec.brain.getNode("input").output)

	def testAllMutate(self):
		''' All Input parameters should mutate.'''
		self.geno.rand.default.floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatValues = [0.5, 0.75]
		self.geno.rand.getContext("mutateFloat").floatDefault = 0.5
		self.geno.getNode("input").mutateParameters()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.assertNotEqual("", self.agentSpec.brain.getNode("input").channel)
		self.assertNotEqual("position", self.agentSpec.brain.getNode("input").integrate)
		self.assertNotEqual([0.0, 1.0], self.agentSpec.brain.getNode("input").range)
		
	def testMutateOutputChannelNotSet(self):
		''' Channel is not set and Output should mutate 
		'''
		
		# channel not set, mutate output
		self.geno.rand.getContext("shouldMutate").floatValues = [ 0.0, 1.0 ]
		self.geno.rand.default.floatDefault = 0.5
		self.geno.getNode("input").mutateValue()
		self.assertEqual("", self.agentSpec.brain.getNode("input").channel)
		self.assertAlmostEqual(0.5, self.agentSpec.brain.getNode("input").output)
		
	def testMutateChannelChannelNotSet(self):
		''' Channel is not set and Channel should mutate 
		'''
		# channel not set, mutate channel
		self.geno.rand.getContext("shouldMutate").floatValues = [ 0.0, 0.0 ]
		self.geno.rand.default.intDefault = 1
		self.geno.getNode("input").mutateValue()
		self.assertEqual(self.geno.inputChannels()[1], self.agentSpec.brain.getNode("input").channel)
		self.assertAlmostEqual(0.0, self.agentSpec.brain.getNode("input").output)

	def testMutateChannelChannelSet(self):
		''' Channel is set and Channel should mutate 
		'''
		# channel set, mutate channel
		self.geno.rand.getContext("shouldMutate").floatValues = [ 0.0, 1.0 ]
		self.geno.rand.default.intDefault = 1
		self.geno.getNode("input").node.channel = self.geno.inputChannels()[0]
		self.geno.getNode("input").mutateValue()
		self.assertEqual(self.geno.inputChannels()[1], self.agentSpec.brain.getNode("input").channel)
		self.assertAlmostEqual(0.0, self.agentSpec.brain.getNode("input").output)

	def testMutateOutputChannelSet(self):
		''' Channel is set and Output should mutate 
		'''
		# channel set, mutate output
		self.geno.rand.getContext("shouldMutate").floatValues = [ 0.0, 0.0 ]
		self.geno.rand.default.floatDefault = 0.5
		self.geno.getNode("input").node.channel = self.geno.inputChannels()[0]
		self.geno.getNode("input").mutateValue()
		self.assertEqual("", self.agentSpec.brain.getNode("input").channel)
		self.assertAlmostEqual(0.5, self.agentSpec.brain.getNode("input").output)


	def testMutateIntegrate(self):
		''' Output integrate should mutate.
			First: 	"speed"
		'''
		self.geno.rand.default.intValues = [ 0, 1 ]
		self.geno.stringMutationRate = 0.99
		self.geno.getNode("input").mutateIntegrate()
		self.assertEqual("speed", self.agentSpec.brain.getNode("input").integrate)

	def testMutateRange(self):
		''' Output range should mutate.
			First: 	[0.5, 0.75]
		'''
		self.geno.rand.getContext("shouldMutate").floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatValues = [0.5, 0.25, 0.75]
		self.geno.getNode("input").mutateRange()
		self.assertEqual([0.5, 0.75], self.agentSpec.brain.getNode("input").range)


suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateInput)


	
