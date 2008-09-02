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
import ns.bridge.data.Brain as Brain

class Node(object):
	def __init__(self, genotype, node):
		self._geno = genotype
		self.node = node
		
	def shouldMutate(self, rate):
		return self._geno.rand.random() < rate
		
	def mutateString(self, curValue, validValues):
		'''	Returns a random string value from validValues.'''
		value = curValue
		while (value == curValue):
			index = self._geno.rand.randint(0, len(validValues) - 1)
			value = validValues[index]
		return value
	
	def mutateFloat(self, curValue):
		'''	Returns a random float value within a gaussian distribution of
			curValue.
			TODO: scale the distribution size in proportion to curValue.'''
		return self._geno.rand.gauss(curValue, 2)
	
	def mutateFloatRange(self, curValue):
		'''	Individually mutates both the min and max of the range, making
			sure that max is greater than or equal to min.'''
		range = [ ]
		range.append(self.mutateFloat(curValue[0]))
		range.append(self.mutateFloat(curValue[1]))
		while range[1] < range[0]:
			range[1] = self.mutateFloat(curValue[1])
		return range


class Output(Node):
	def __init__(self, genotype, node):
		super(Output, self).__init__(genotype, node)

	def mutate(self):
		self.mutateChannel()
		self.mutateIntegrate()
		self.mutateManual()
		self.mutateDefuzz()
		self.mutateRange()
		self.mutateDelay()
		self.mutateRate()
		self.mutateOutput()
		
	def mutateChannel(self):
		''' Channel (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.channel = self.mutateString(self.node.channel, self._geno.outputChannels())

	def mutateIntegrate(self):
		''' Integrate (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.integrate = self.mutateString(self.node.integrate, Brain.Output.kIntegrateValues)

	def mutateManual(self):
		''' Manual (bool)'''
		if self.shouldMutate(self._geno.boolMutationRate):
			self.node.manual = not self.node.manual

	def mutateDefuzz(self):
		''' Defuzz (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.defuzz = self.mutateString(self.node.defuzz, Brain.Output.kDefuzzValues)

	def mutateRange(self):
		''' Range (float, float)'''
		if self.shouldMutate(self._geno.rangeMutationRate):
			self.node.range = self.mutateFloatRange(self.node.range)

	def mutateDelay(self):
		''' Delay (float)'''
		if self.shouldMutate(self._geno.floatMutationRate):
			self.node.delay = self.mutateFloat(self.node.delay)

	def mutateRate(self):
		''' Rate (float)
			aka: filter'''
		if self.shouldMutate(self._geno.floatMutationRate):
			self.node.rate = self.mutateFloat(self.node.rate)

	def mutateOutput(self):
		''' Output (float)
			Only allowed to mutate if Output node is not connected and Manual
			is set.'''
		if (self.node.manual and
		  	not self.node.inputs and
		  	not self.node.altInputs and
		  	self.shouldMutate(self._geno.floatMutationRate)):
			self.node.output = self.mutateFloat(self.node.output)

class Defuzz(Node):
	def __init__(self, genotype, node):
		super(Defuzz, self).__init__(genotype, node)

	def mutate(self):
		self.mutateDefuzz()
		self.mutateElse()
		
	def mutateDefuzz(self):
		''' Defuzz (float)'''
		if self.shouldMutate(self._geno.floatMutationRate):
			self.node.defuzz = self.mutateFloat(self.node.defuzz)

	def mutateElse(self):
		''' Else (bool)'''
		if self.shouldMutate(self._geno.boolMutationRate):
			self.node.isElse = not self.node.isElse
