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

class Node(object):
	def __init__(self, genotype, node):
		self._geno = genotype
		self._node = node
		
	def shouldMutate(self, rate):
		return self._geno.rand.random() < rate
		
	def mutateString(self, curValue, validValues):
		'''	Returns a random string value from validValues.'''
		index = self._geno.rand.randint(0, len(validValues))
		return validValues[index]


class Output(Node):
	def __init__(self, genotype, node):
		super(Output, self).__init__(genotype, node)

	def mutate(self):
		# output channel
		if self.shouldMutate(self._geno.stringMutationRate()):
			self._node.channel = self.mutateString(self._node.channel, self._geno.outputChannels())
