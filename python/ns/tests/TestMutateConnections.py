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


class TestMutateConnections(unittest.TestCase):
	
	def setUp(self):
		input = "R:/massive/testdata/cdl/man/CDL/connections.cdl"
		self.agentSpec = CDLReader.read(input, CDLReader.kEvolveTokens)
		self.geno = Genotype.Genotype(self.agentSpec)
		self.geno.rand = TestUtil.NotRandom()
		
	def tearDown(self):
		try:
			pass
		except:
			pass
	
	def testNoMutate(self):
		''' No connections should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(7, len(nodes))
		
		self.geno.rand.default.floatDefault = 0.1
		
		self.geno.getNode("both").mutateConnections()
		self.geno.getNode("reg").mutateConnections()
		self.geno.getNode("alt").mutateConnections()
		
		self.assertEqual([1, 2], self.agentSpec.brain.getNode("both").inputs)
		self.assertEqual([3], self.agentSpec.brain.getNode("both").altInputs)
		self.assertEqual([1], self.agentSpec.brain.getNode("reg").inputs)
		self.assertEqual([], self.agentSpec.brain.getNode("reg").altInputs)
		self.assertEqual([], self.agentSpec.brain.getNode("alt").inputs)
		self.assertEqual([3, 2], self.agentSpec.brain.getNode("alt").altInputs)

	def testAllMutate(self):
		''' All connections should mutate.'''
		nodes = self.agentSpec.brain.nodes()
		self.assertEqual(7, len(nodes))
		
		self.geno.rand.default.floatDefault = 0.0
		
		self.geno.getNode("both").mutateConnections()
		self.geno.getNode("reg").mutateConnections()
		self.geno.getNode("alt").mutateConnections()
		
		self.assertEqual(2, len(self.agentSpec.brain.getNode("both").inputs))
		self.assertNotEqual(1, self.agentSpec.brain.getNode("both").inputs[0])
		self.assertNotEqual(2, self.agentSpec.brain.getNode("both").inputs[1])
		
		self.assertEqual(1, len(self.agentSpec.brain.getNode("both").altInputs))
		self.assertNotEqual(3, self.agentSpec.brain.getNode("both").altInputs[0])

		self.assertEqual(1, len(self.agentSpec.brain.getNode("reg").inputs))
		self.assertNotEqual(1, self.agentSpec.brain.getNode("reg").inputs[0])
		
		self.assertEqual(0, len(self.agentSpec.brain.getNode("reg").altInputs))
		self.assertEqual([], self.agentSpec.brain.getNode("reg").altInputs)
		
		self.assertEqual(0, len(self.agentSpec.brain.getNode("alt").inputs))
		self.assertEqual([], self.agentSpec.brain.getNode("alt").inputs)
		
		self.assertEqual(2, len(self.agentSpec.brain.getNode("alt").altInputs))
		self.assertNotEqual(3, self.agentSpec.brain.getNode("alt").altInputs[0])
		self.assertNotEqual(2, self.agentSpec.brain.getNode("alt").altInputs[1])

	def testRegularConnection(self):
		''' Test nodes that we can't reconnect a regular connection to.'''
		self.geno.rand.default.floatDefault = 0.0
		self.geno.rand.default.intValues = [0,	# same node
										  	1, 	# already have a regular connection
										  	2, 	# already have an alt connection
										  	4, 	# ourself
										  	3]
		
		self.geno.getNode("both").mutateConnections()
		self.assertEqual(4, self.agentSpec.brain.getNode("both").inputs[0])

	def testAltConnection(self):
		''' Test nodes that we can't reconnect an altconnection to.'''
		self.geno.rand.default.floatValues = [1.0,	# don't mutate regular
											  1.0, 	# don't mutate regular
											  0.0]
		self.geno.rand.default.intValues = [2,	# same node
										  	0, 	# already have a regular connection
										  	4, 	# ourself
										  	3]
		
		self.geno.getNode("both").mutateConnections()
		self.assertEqual(4, self.agentSpec.brain.getNode("both").altInputs[0])


suite = unittest.TestLoader().loadTestsFromTestCase(TestMutateConnections)


	
