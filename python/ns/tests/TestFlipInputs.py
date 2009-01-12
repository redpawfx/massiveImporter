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


class TestFlipInputs(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/flip_inputs.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
    # defuzz reg:  no mutation
    #              regular becomes alt
    # defuzz alt:  no mutation
    #              alt becomes regular
    # or:          no mutation
    #              regular becomes alt, alt stays
    #              regular becomes alt, alt becomes regular
    #              alt becomes regular, regular stays
	# and:		   no mutation
	#			   regular becomes alt, alt stays
	#			   regular becomes alt, alt becomes regular
	#			   alt becomes regular, regular stays
	# fuzz:        no mutations
	# noise:       no mutations
	# timer both:  no mutation
    #              alt becomes regular, regular becomes alt
    #              alt doesn't become regular, stays
    #              regular doesn't become alt, stays
    # timer reg:   no mutation
    #              regular becomes alt
    # timer alt:   no mutation
    #              alt becomes regular
    # input:       no mutatio
     
	def testFlipOutput(self):
		'''	Output: No mutations. Output nodes do not have altInputs
		'''
		self.geno.rand.default.floatDefault = 0.0
		
		self.geno.getNode("output").flipInputs()
		
		self.assertEqual([1], self.agentSpec.brain.getNode("output").inputs)
		self.assertEqual([], self.agentSpec.brain.getNode("output").altInputs)
		
	def testFlipDefuzzElse(self):
		'''	Defuzz Else: No mutations. Defuzz else nodes do not have altInputs
		'''
		self.geno.rand.default.floatDefault = 0.0
		
		self.geno.getNode("defuzz_else").flipInputs()
		
		self.assertEqual([], self.agentSpec.brain.getNode("defuzz_else").inputs)
		self.assertEqual([], self.agentSpec.brain.getNode("defuzz_else").altInputs)

	def testFlipDefuzzBothA(self):
		'''	Defuzz Both: No mutations.
		'''
		self.geno.rand.default.floatDefault = 1.0
		
		self.geno.getNode("defuzz_both").flipInputs()
		
		self.assertEqual([2], self.agentSpec.brain.getNode("defuzz_both").inputs)
		self.assertEqual([3], self.agentSpec.brain.getNode("defuzz_both").altInputs)

	def testFlipDefuzzBothB(self):
		'''	Defuzz Both: Alt become regular, regular stays.
		'''
		self.geno.rand.default.floatValues = [0.0, 1.0]
		
		self.geno.getNode("defuzz_both").flipInputs()
		
		self.assertEqual([2, 3], self.agentSpec.brain.getNode("defuzz_both").inputs)
		self.assertEqual([], self.agentSpec.brain.getNode("defuzz_both").altInputs)

	def testFlipDefuzzBothC(self):
		'''	Defuzz Both: Alt become regular, regular becomes alt.
		'''
		self.geno.rand.default.floatValues = [0.0, 0.0]
		
		self.geno.getNode("defuzz_both").flipInputs()
		
		self.assertEqual([3], self.agentSpec.brain.getNode("defuzz_both").inputs)
		self.assertEqual([2], self.agentSpec.brain.getNode("defuzz_both").altInputs)

	def testFlipDefuzzBothD(self):
		'''	Defuzz Both: Alt doesn't flip so regular can't
		'''
		self.geno.rand.default.floatValues = [1.0, 0.0]
		
		self.geno.getNode("defuzz_both").flipInputs()
		
		self.assertEqual([2], self.agentSpec.brain.getNode("defuzz_both").inputs)
		self.assertEqual([3], self.agentSpec.brain.getNode("defuzz_both").altInputs)

	def testFlipDefuzzRegA(self):
		'''	Defuzz Reg: No mutations.
		'''
		self.geno.rand.default.floatDefault = 1.0
		
		self.geno.getNode("defuzz_reg").flipInputs()
		
		self.assertEqual([2], self.agentSpec.brain.getNode("defuzz_reg").inputs)
		self.assertEqual([], self.agentSpec.brain.getNode("defuzz_reg").altInputs)

	def testFlipDefuzzRegB(self):
		'''	Defuzz Reg: Regular becomes alt
		'''
		self.geno.rand.default.floatDefault = 0.0
		
		self.geno.getNode("defuzz_reg").flipInputs()
		
		self.assertEqual([], self.agentSpec.brain.getNode("defuzz_reg").inputs)
		self.assertEqual([2], self.agentSpec.brain.getNode("defuzz_reg").altInputs)



suite = unittest.TestLoader().loadTestsFromTestCase(TestFlipInputs)
