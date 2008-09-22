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
import random

import ns.bridge.data.Brain as Brain
import ns.evolve.Mutate as Mutate
import ns.py.Errors as Errors

class Random(object):
	'''	A class to wrap the python random generator. This is so that I can
		define a fake random generator for testing purposes. '''
	def randint(self, a, b):
		return random.randint(a, b)
	
	def random(self):
		return random.random()
	
	def uniform(self, a, b):
		return random.uniform(a, b)
	
	def gauss(self, mu, sigma):
		return random.gauss(mu, sigma)

class Genotype(object):
	def __init__(self, agentSpec):
		self.agentSpec = agentSpec
		self.rand = Random()
		
		self._stringRate = 0.1
		self._boolRate = 0.1
		self._rangeRate = 0.1
		self._floatRate = 0.1
		self._listRate = 0.1
		self._nodes = []
		self._outputChannels = []
		
		self._initNodes()
		self._initOutputChannels()
		
	def _setStringMutationRate(self, val):
		self._stringRate = val
	def _getStringMutationRate(self): return self._stringRate
	stringMutationRate = property(_getStringMutationRate, _setStringMutationRate)
		
	def _setBoolMutationRate(self, val):
		self._boolRate = val
	def _getBoolMutationRate(self): return self._boolRate
	boolMutationRate = property(_getBoolMutationRate, _setBoolMutationRate)

	def _setRangeMutationRate(self, val):
		self._rangeRate = val
	def _getRangeMutationRate(self): return self._rangeRate
	rangeMutationRate = property(_getRangeMutationRate, _setRangeMutationRate)

	def _setFloatMutationRate(self, val):
		self._floatRate = val
	def _getFloatMutationRate(self): return self._floatRate
	floatMutationRate = property(_getFloatMutationRate, _setFloatMutationRate)

	def _setListMutationRate(self, val):
		self._listRate = val
	def _getListMutationRate(self): return self._listRate
	listMutationRate = property(_getListMutationRate, _setListMutationRate)
	
	def _initNodes(self):
		'''	Build a Mutate node for each Brain node. '''
		for node in self.agentSpec.brain.nodes():
			if isinstance(node, Brain.Output):
				self._nodes.append(Mutate.Output(self, node))
			if isinstance(node, Brain.Defuzz):
				self._nodes.append(Mutate.Defuzz(self, node))
			if isinstance(node, Brain.Or):
				self._nodes.append(Mutate.Or(self, node))
			if isinstance(node, Brain.Rule):
				self._nodes.append(Mutate.Rule(self, node))
			if isinstance(node, Brain.Fuzz):
				self._nodes.append(Mutate.Fuzz(self, node))
			if isinstance(node, Brain.Noise):
				self._nodes.append(Mutate.Noise(self, node))
				
	def _initOutputChannels(self):
		'''	defaultChannels +
			action + action:rate + action1->action2 +
			variable
			Only variables without expressions are included. '''
			
		# default channels
		self._outputChannels = [ "ty", "rx", "ry", "rz" ]
		
		# action + action:rate + action1->action2
		for action in self.agentSpec.actions.values():
			self._outputChannels.append(action.name)
			self._outputChannels.append("%s:rate" % action.name)
			for blend in self.agentSpec.actions.values():
				if action.name != blend.name:
					self._outputChannels.append("%s->%s" % (action.name, blend.name))
					
		# variables without expressions
		for variable in self.agentSpec.variables.values():
			if not variable.expression:
				self._outputChannels.append(variable.name)
		
	def mutate(self):
		for node in self._nodes:
			node.mutate()
			
	def getNode(self, name):
		for n in self._nodes:
			if n.node.name == name:
				return n
		raise Errors.Error("No node named %s" % name)

	def outputChannels(self):
		'''	Return a list of all possible output channels. Includes actions,
			variables, and built-in channels.'''
		return self._outputChannels
	
	
