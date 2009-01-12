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


class TestMutateNoise(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/noise.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No Noise parameters should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.geno.rand.default.floatDefault = 0.1
		
		self.geno.getNode("noise").mutateParameters()
		
		node = self.agentSpec.brain.getNode("noise")
		self.assertAlmostEqual(0.5, node.rate)

	def testAllMutate(self):
		''' All Noise parameters should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.geno.rand.default.floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatDefault = 0.1
		
		self.geno.getNode("noise").mutateParameters()
		
		node = self.agentSpec.brain.getNode("noise")
		self.assertNotAlmostEqual(0.5, node.rate)

	def testMutateRate(self):
		''' Noise rate should mutate.
			First: 	0.5
		'''
		self.geno.rand.default.floatDefault = 0.1
		self.geno.floatMutationRate = 0.99
		self.geno.getNode("noise").mutateRate()
		self.assertAlmostEqual(0.1, self.agentSpec.brain.getNode("noise").rate)

suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateNoise)


	
