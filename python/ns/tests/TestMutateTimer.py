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


class TestMutateTimer(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/timer.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No Timer parameters should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.geno.rand.getContext("shouldMutate").floatDefault = 0.1
		
		self.geno.getNode("timer").mutateParameters()
		
		node = self.agentSpec.brain.getNode("timer")
		self.assertAlmostEqual(1.0, node.rate)
		self.assertEqual("if_stopped", node.trigger)
		self.assertEqual([0.0, 1.0], node.range)
		self.assertEqual(False, node.endless)

	def testAllMutate(self):
		''' All Timer parameters should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))

		self.geno.rand.getContext("shouldMutate").floatDefault = 0.0
		
		self.geno.getNode("timer").mutateParameters()
		
		node = self.agentSpec.brain.getNode("timer")
		self.assertNotAlmostEqual(1.0, node.rate)
		self.assertNotEqual("if_stopped", node.trigger)
		self.assertNotEqual([0.0, 1.0], node.range)
		self.assertNotEqual(False, node.endless)

	def testMutateRate(self):
		''' Timer rate should mutate.
			First: 	0.5
		'''
		self.geno.rand.default.floatDefault = 0.5
		self.geno.floatMutationRate = 0.99
		self.geno.getNode("timer").mutateRate()
		self.assertAlmostEqual(0.5, self.agentSpec.brain.getNode("timer").rate)

	def testMutateTrigger(self):
		''' Timer trigger should mutate.
			First: always
		'''
		self.geno.rand.default.floatDefault = 0.0
		self.geno.rand.default.intDefault = 1
		self.geno.getNode("timer").mutateTrigger()
		self.assertEqual("always", self.agentSpec.brain.getNode("timer").trigger)

	def testMutateRange(self):
		''' Output range should mutate.
			First: 	[0.5, 0.75]
		'''
		self.geno.rand.getContext("shouldMutate").floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatValues = [0.5, 0.25, 0.75]
		self.geno.getNode("timer").mutateRange()
		self.assertEqual([0.5, 0.75], self.agentSpec.brain.getNode("timer").range)

	def testMutateEndless(self):
		''' Defuzz endless should mutate.
			First: 	True
		'''
		self.geno.boolMutationRate = 0.99
		self.geno.getNode("timer").mutateEndless()
		self.assertEqual(True, self.agentSpec.brain.getNode("timer").endless)

suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateTimer)


	
