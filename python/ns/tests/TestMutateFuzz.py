# The MIT License
#	
# Copyright (c) 2008 James Piechota
#	
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software fuzz associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, fuzz/fuzz sell
# copies of the Software, fuzz to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice fuzz this permission notice shall be included in
# all copies fuzz substantial portions of the Software.
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


class TestMutateFuzz(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/fuzz.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No Fuzz parameters should mutate.'''
		self.geno.rand.default.floatRandom = False
		self.geno.rand.default.floatDefault = 0.1
		self.geno.mutate()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.assertEqual("lamda", self.agentSpec.brain.getNode("fuzz").inference)
		self.assertEqual([0.25, 0.5, 0.75], self.agentSpec.brain.getNode("fuzz").inferencePoints)
		self.assertEqual("cosine", self.agentSpec.brain.getNode("fuzz").interpolation)
		self.assertEqual(False, self.agentSpec.brain.getNode("fuzz").wrap)

	def testAllMutate(self):
		''' All Fuzz parameters should mutate.'''
		self.geno.rand.getContext("shouldMutate").floatRandom = False
		self.geno.rand.getContext("shouldMutate").floatDefault = 0.0
		self.geno.mutate()
		
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(1, len(nodes))
		
		self.assertNotEqual("lamda", self.agentSpec.brain.getNode("fuzz").inference)
		self.assertNotEqual([0.25, 0.5, 0.75], self.agentSpec.brain.getNode("fuzz").inferencePoints)
		self.assertNotEqual("cosine", self.agentSpec.brain.getNode("fuzz").interpolation)
		self.assertNotEqual(False, self.agentSpec.brain.getNode("fuzz").wrap)

	def testMutateCurveInference1(self):
		''' Fuzz inference should mutate triggering the points to mutate (more points).
		'''
		self.geno.rand.getContext("shouldMutate").floatRandom = False
		self.geno.rand.getContext("shouldMutate").floatValues = [ 0.0, 1.0 ]
		self.geno.rand.getContext("mutateString").intRandom = False
		self.geno.rand.getContext("mutateString").intDefault = 2
		self.geno.getNode("fuzz").mutateCurve()
		self.assertEqual("pi", self.agentSpec.brain.getNode("fuzz").inference)
		points = self.agentSpec.brain.getNode("fuzz").inferencePoints
		self.assertNotEqual([0.25, 0.5, 0.75], points)
		self.assertEqual(4, len(points))
		self.assert_(points[1] > points[0])
		self.assert_(points[2] > points[1])
		self.assert_(points[3] > points[2])

	def testMutateCurveInference2(self):
		''' Fuzz inference should mutate triggering the points to mutate (fewer points).
		'''
		self.geno.rand.getContext("shouldMutate").floatRandom = False
		self.geno.rand.getContext("shouldMutate").floatValues = [ 0.0, 1.0 ]
		self.geno.rand.getContext("mutateString").intRandom = False
		self.geno.rand.getContext("mutateString").intDefault = 0
		self.geno.rand.default.floatValues = [ 0.5, 0.4, 0.5, 0.8 ]
		self.geno.getNode("fuzz").mutateCurve()
		self.assertEqual("z", self.agentSpec.brain.getNode("fuzz").inference)
		points = self.agentSpec.brain.getNode("fuzz").inferencePoints
		self.assertEqual(2, len(points))
		self.assertAlmostEqual(0.5, points[0])
		self.assertAlmostEqual(0.8, points[1])

	def testMutateCurvePoints(self):
		''' Fuzz inference points should mutate even though inference type did
			not
		'''
		self.geno.rand.getContext("shouldMutate").floatRandom = False
		self.geno.rand.getContext("shouldMutate").floatValues = [ 1.0, 0.0 ]
		self.geno.rand.getContext("mutateString").intRandom = False
		self.geno.rand.getContext("mutateString").intDefault = 2
		self.geno.getNode("fuzz").mutateCurve()
		self.assertEqual("lamda", self.agentSpec.brain.getNode("fuzz").inference)
		points = self.agentSpec.brain.getNode("fuzz").inferencePoints
		self.assertNotEqual([0.25, 0.5, 0.75], points)
		self.assertEqual(3, len(points))
		self.assert_(points[1] > points[0])
		self.assert_(points[2] > points[1])

	def testMutateInterpolation(self):
		''' Fuzz interpolation should mutate.
			First: 	"linear"
		'''
		self.geno.stringMutationRate = 0.99
		self.geno.getNode("fuzz").mutateInterpolation()
		self.assertEqual("linear", self.agentSpec.brain.getNode("fuzz").interpolation)

	def testMutateWrap(self):
		''' Fuzz wrap should mutate.
			First: True
		'''
		self.geno.rand.default.floatRandom = False
		self.geno.rand.default.floatDefault = 0.0
		self.geno.getNode("fuzz").mutateWrap()
		self.assertEqual(True, self.agentSpec.brain.getNode("fuzz").wrap)

suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateFuzz)


	
