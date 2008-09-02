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


class TestMutateDefuzz(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/defuzz.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No Defuzz parameters should mutate.'''
		self.geno.rand.default.floatDefault = 0.1
		self.geno.mutate()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.assertEqual(False, self.agentSpec.brain.getNode("defuzz").isElse)
		self.assertAlmostEqual(0.0, self.agentSpec.brain.getNode("defuzz").defuzz)

	def testAllMutate(self):
		''' All Defuzz parameters should mutate.'''
		self.geno.rand.default.floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatDefault = 0.5
		self.geno.mutate()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.assertNotEqual(False, self.agentSpec.brain.getNode("defuzz").isElse)
		self.assertNotAlmostEqual(0.0, self.agentSpec.brain.getNode("defuzz").defuzz)

	def testMutateDefuzz(self):
		''' Defuzz defuzz should mutate.
			First: 	0.5
		'''
		self.geno.rand.default.floatDefault = 0.5
		self.geno.floatMutationRate = 0.99
		self.geno.getNode("defuzz").mutateDefuzz()
		self.assertAlmostEqual(0.5, self.agentSpec.brain.getNode("defuzz").defuzz)

	def testMutateElse(self):
		''' Defuzz else should mutate.
			First: 	True
		'''
		self.geno.boolMutationRate = 0.99
		self.geno.getNode("defuzz").mutateElse()
		self.assertEqual(True, self.agentSpec.brain.getNode("defuzz").isElse)

suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateDefuzz)


	
