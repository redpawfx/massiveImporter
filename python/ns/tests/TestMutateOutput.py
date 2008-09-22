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


class TestMutateOutput(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/output.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No Output parameters should mutate.'''
		self.geno.rand.default.floatDefault = 0.1
		self.geno.getNode("unconnected").mutate()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(5, len(nodes))
		
		self.assertEqual("channel", self.agentSpec.brain.getNode("unconnected").channel)
		self.assertEqual("position", self.agentSpec.brain.getNode("unconnected").integrate)
		self.assertEqual(False, self.agentSpec.brain.getNode("unconnected").manual)
		self.assertEqual("COM", self.agentSpec.brain.getNode("unconnected").defuzz)
		self.assertEqual([0.0, 1.0], self.agentSpec.brain.getNode("unconnected").range)
		self.assertAlmostEqual(0.0, self.agentSpec.brain.getNode("unconnected").delay)
		self.assertAlmostEqual(0.0, self.agentSpec.brain.getNode("unconnected").rate)
		self.assertAlmostEqual(1.0, self.agentSpec.brain.getNode("unconnected").output)

	def testAllMutate(self):
		''' All Output parameters should mutate.'''
		self.geno.rand.default.floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatValues = [0.5, 0.75]
		self.geno.rand.getContext("mutateFloat").floatDefault = 0.5
		self.geno.getNode("unconnected").mutate()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(5, len(nodes))
		
		self.assertNotEqual("channel", self.agentSpec.brain.getNode("unconnected").channel)
		self.assertNotEqual("position", self.agentSpec.brain.getNode("unconnected").integrate)
		self.assertNotEqual(False, self.agentSpec.brain.getNode("unconnected").manual)
		self.assertNotEqual("COM", self.agentSpec.brain.getNode("unconnected").defuzz)
		self.assertNotEqual([0.0, 1.0], self.agentSpec.brain.getNode("unconnected").range)
		self.assertNotAlmostEqual(0.0, self.agentSpec.brain.getNode("unconnected").delay)
		self.assertNotAlmostEqual(0.0, self.agentSpec.brain.getNode("unconnected").rate)
		self.agentSpec.brain.getNode("unconnected").manual = True
		self.assertNotAlmostEqual(1.0, self.agentSpec.brain.getNode("unconnected").output)
		
	def testMutateChannel(self):
		''' Output channel should mutate.
			First: 	"ty"
			Second:	"rx" - skips "ty" since it is unchanged
			Third:	"walk_sad->walk_45L"	 
		'''
		self.geno.rand.default.intValues = [ 0 ]
		self.geno.stringMutationRate = 0.99

		self.geno.getNode("unconnected").mutateChannel()
		self.assertEqual("ty", self.agentSpec.brain.getNode("unconnected").channel)
		
		self.geno.rand.default.intValues = [ 0, 1 ]
		self.geno.getNode("unconnected").mutateChannel()
		self.assertEqual("rx", self.agentSpec.brain.getNode("unconnected").channel)

		self.geno.rand.default.intValues = [ 10 ]
		self.geno.getNode("unconnected").mutateChannel()
		self.assertEqual("walk_sad->walk_45L", self.agentSpec.brain.getNode("unconnected").channel)

	def testMutateIntegrate(self):
		''' Output integrate should mutate.
			First: 	"speed"
		'''
		self.geno.rand.default.intValues = [ 0, 1 ]
		self.geno.stringMutationRate = 0.99
		self.geno.getNode("unconnected").mutateIntegrate()
		self.assertEqual("speed", self.agentSpec.brain.getNode("unconnected").integrate)

	def testMutateManual(self):
		''' Output manual should mutate.
			First: 	True
		'''
		self.geno.boolMutationRate = 0.99
		self.geno.getNode("unconnected").mutateManual()
		self.assertEqual(True, self.agentSpec.brain.getNode("unconnected").manual)

	def testMutateDefuzz(self):
		''' Output defuzz should mutate.
			First: 	BLEND
		'''
		self.geno.rand.default.intValues = [ 0, 2 ]
		self.geno.stringMutationRate = 0.99
		self.geno.getNode("unconnected").mutateDefuzz()
		self.assertEqual("BLEND", self.agentSpec.brain.getNode("unconnected").defuzz)

	def testMutateRange(self):
		''' Output range should mutate.
			First: 	[0.5, 0.75]
		'''
		self.geno.rand.getContext("shouldMutate").floatRandom = False
		self.geno.rand.getContext("shouldMutate").floatDefault = 0.0
		self.geno.rand.getContext("mutateFloat").floatValues = [0.5, 0.25, 0.75]
		self.geno.getNode("unconnected").mutateRange()
		self.assertEqual([0.5, 0.75], self.agentSpec.brain.getNode("unconnected").range)

	def testMutateDelay(self):
		''' Output delay should mutate.
			First: 	0.5
		'''
		self.geno.rand.default.floatRandom = False
		self.geno.rand.default.floatDefault = 0.5
		self.geno.floatMutationRate = 0.99
		self.geno.getNode("unconnected").mutateDelay()
		self.assertAlmostEqual(0.5, self.agentSpec.brain.getNode("unconnected").delay)

	def testMutateRate(self):
		''' Output rate should mutate.
			First: 	0.5
		'''
		self.geno.rand.getContext("mutateFloat").floatDefault = 0.5
		self.geno.floatMutationRate = 0.99
		self.geno.getNode("unconnected").mutateRate()
		self.assertAlmostEqual(0.5, self.agentSpec.brain.getNode("unconnected").rate)

	def testMutateConnectedOutput(self):
		'''	Output should not mutate since Output node is connected.
		'''
		self.geno.floatMutationRate = 0.99
		self.geno.getNode("connected").mutateOutput()
		self.assertAlmostEqual(0.0, self.agentSpec.brain.getNode("connected").output)

	def testMutateNonManualOutput(self):
		'''	Output should not mutate since Output node is not manual.
		'''
		self.geno.floatMutationRate = 0.99
		self.agentSpec.brain.getNode("unconnected").manual = False
		self.geno.getNode("unconnected").mutateOutput()
		self.assertAlmostEqual(1.0, self.agentSpec.brain.getNode("unconnected").output)

	def testMutateManualOutput(self):
		'''	Output should mutate since Output node is manual.
		'''
		self.geno.floatMutationRate = 0.99
		self.geno.rand.default.floatDefault = 0.1
		self.agentSpec.brain.getNode("unconnected").manual = True
		self.geno.getNode("unconnected").mutateOutput()
		self.assertAlmostEqual(0.1, self.agentSpec.brain.getNode("unconnected").output)

suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateOutput)


	
