# The MIT License
#	
# Copyright (c) 2008 James Piechota
#	
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/and sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies and substantial portions of the Software.
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


class TestMutateAnd(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/and.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No And parameters should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.geno.rand.default.floatDefault = 0.1
		
		self.geno.getNode("and").mutateParameters()
		
		node = self.agentSpec.brain.getNode("and")
		self.assertAlmostEqual(1.0, node.weight)
		self.assertEqual("min", node.type)

	def testAllMutate(self):
		''' All And parameters should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))

		self.geno.rand.default.floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatDefault = 0.5
		
		self.geno.getNode("and").mutateParameters()
		
		node = self.agentSpec.brain.getNode("and")
		self.assertNotAlmostEqual(1.0, node.weight)
		self.assertNotEqual("max", node.type)

	def testMutateWeight(self):
		''' And weight should mutate.
			First: 	0.5
		'''
		self.geno.rand.default.floatDefault = 0.5
		self.geno.floatMutationRate = 0.99
		self.geno.getNode("and").mutateWeight()
		self.assertAlmostEqual(0.5, self.agentSpec.brain.getNode("and").weight)

	def testMutateType(self):
		''' And type should mutate.
			First: 	"prod"
		'''
		self.geno.stringMutationRate = 0.99
		self.geno.getNode("and").mutateType()
		self.assertEqual("prod", self.agentSpec.brain.getNode("and").type)

suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateAnd)


	
