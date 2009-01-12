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
		
	def mutate(self):
		self.mutateParameters()
		self.mutateInputs()
		
	def mutateInputs(self):
		''' 1. reconnect inputs to other nodes
			2. flip regular inputs to alt-inputs, and vice versa
		'''
		self.mutateConnections()
		self.flipInputs()
			
	def mutateConnections(self):
		for i in range(len(self.node.inputs)):
			if self.shouldMutate(self._geno.reconnectRate):
				newSrc = self.reconnect(self.node.inputs[i])
				self.node.inputs[i] = newSrc.id
		for i in range(len(self.node.altInputs)):
			if self.shouldMutate(self._geno.reconnectRate):
				newSrc = self.reconnect(self.node.altInputs[i])
				self.node.altInputs[i] = newSrc.id
			
	def reconnect(self, oldSrcId):
		'''	Disconnect from oldSrc, and find a new source node to reconnect to.
		'''
		# notify the source node that it's losing an output connection
		oldSrc = self._geno.getNode(oldSrcId).node
		oldSrc.disconnect(self.node)
		# find a random node, not ourself, to reconnect to
		nodes = self._geno.getNodes()
		while True:
			index = self._geno.rand.randint(0, len(nodes)-1)
			# notify the new source node that it's gaining an output
			# connection
			newSrc = nodes[index].node
			if (newSrc != self.node and
			 	newSrc != oldSrc and
			 	newSrc.id not in self.node.inputs and
			 	newSrc.id not in self.node.altInputs):
				break
		newSrc.connect(self.node)
		return newSrc
		
	def shouldMutate(self, rate):
		return self._geno.rand.random() < rate
	
	def mutateString(self, curValue, validValues):
		'''	Returns a random string value from validValues.'''
		value = curValue
		while (value == curValue):
			value = validValues[self._geno.rand.randint(0, len(validValues)-1)]
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

	def mutateFloatList(self, numValues, curValues):
		list = []
		for i in range(numValues):
			while(True):
				if i < len(curValues):
					val = self.mutateFloat(curValues[i])
				else:
					val = self._geno.rand.uniform(list[i-1], list[i-1] * 2)
				if (i == 0 or val > list[i-1]):
					break
			list.append(val)
		return list
				
###############################################################################
# Output
###############################################################################
class Output(Node):
	def __init__(self, genotype, node):
		super(Output, self).__init__(genotype, node)
		
	def mutateParameters(self):
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
			
	def flipInputs(self):
		''' No alt-inputs allows, so no mutations will occur.
		'''
		pass

###############################################################################
# Defuzz
###############################################################################
class Defuzz(Node):
	def __init__(self, genotype, node):
		super(Defuzz, self).__init__(genotype, node)

	def mutateParameters(self):
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
			
	def flipInputs(self):
		''' No alt-inputs allowed if it is an else node, otherwise one
			alt-input allowed. Possibility to flip a single alt-input into
			regular input, and, if no alt-input is present, possibility to
			flip a regular input into an alt-input.
		'''
		if not self.node.isElse:
			# Occasionally flip an alt input into a regular input
			# grab the current input length so we don't flip any
			# inputs back and forth
			numInputs = len(self.node.inputs)
			if self.node.altInputs and self.shouldMutate(self._geno.flipInputRate):
				self.node.inputs.append(self.node.altInputs.pop())
			# If there aren't any alt inputs, occasionally flip a regular
			# input into an alt input
			if (not self.node.altInputs and
			  	self.shouldMutate(self._geno.flipInputRate)):
				index = self._geno.rand.randint(0, numInputs - 1)
				value = self.node.inputs.pop(index)
				self.node.altInputs.append(value)

###############################################################################
# Or
###############################################################################
class Or(Node):
	def __init__(self, genotype, node):
		super(Or, self).__init__(genotype, node)

	def mutateParameters(self):
		self.mutateWeight()
		self.mutateType()
		
	def mutateWeight(self):
		''' Weight (float)'''
		if self.shouldMutate(self._geno.floatMutationRate):
			self.node.weight = self.mutateFloat(self.node.weight)

	def mutateType(self):
		''' Type (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.type = self.mutateString(self.node.type, Brain.Or.kTypeValues)

	def flipInputs(self):
		''' Infinite alt-input allowed. Each input can be flipped into an
			alt-input, and each alt-input can be flipped into a regular input.
		'''
		# record the current number of inputs, since the inputs list may be
		# extended by flipped alt-inputs and we don't want those new inputs
		# to be flipped again
		numInputs = len(self.node.inputs)
		# iterate through the list from end to beginning so that our iteration
		# isn't confused when we remove elements from the list
		for i in range(len(self.node.altInputs), 0, -1):
			if self.shouldMutate(self._geno.flipInputRate):
				self.node.inputs.append(self.node.altInputs.pop(i-1))
		for i in range(numInputs, 0, -1):
			if self.shouldMutate(self._geno.flipInputRate):
				self.node.altInputs.append(self.node.inputs.pop(i-1))

###############################################################################
# Rule
###############################################################################
class Rule(Node):
	def __init__(self, genotype, node):
		super(Rule, self).__init__(genotype, node)

	def mutateParameters(self):
		self.mutateWeight()
		self.mutateType()
		
	def mutateWeight(self):
		''' Weight (float)'''
		if self.shouldMutate(self._geno.floatMutationRate):
			self.node.weight = self.mutateFloat(self.node.weight)

	def mutateType(self):
		''' Type (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.type = self.mutateString(self.node.type, Brain.Rule.kTypeValues)


	def flipInputs(self):
		''' Infinite alt-input allowed. Each input can be flipped into an
			alt-input, and each alt-input can be flipped into a regular input.
		'''
		# record the current number of inputs, since the inputs list may be
		# extended by flipped alt-inputs and we don't want those new inputs
		# to be flipped again
		numInputs = len(self.node.inputs)
		# iterate through the list from end to beginning so that our iteration
		# isn't confused when we remove elements from the list
		for i in range(len(self.node.altInputs), 0, -1):
			if self.shouldMutate(self._geno.flipInputRate):
				self.node.inputs.append(self.node.altInputs.pop(i-1))
		for i in range(numInputs, 0, -1):
			if self.shouldMutate(self._geno.flipInputRate):
				self.node.altInputs.append(self.node.inputs.pop(i-1))

###############################################################################
# Fuzz
###############################################################################
class Fuzz(Node):
	def __init__(self, genotype, node):
		super(Fuzz, self).__init__(genotype, node)

	def mutateParameters(self):
		self.mutateCurve()
		self.mutateInterpolation()
		self.mutateWrap()
		
	def mutateCurve(self):
		''' Inference (String) Points (float(s))'''
		mutatePoints = False
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.inference = self.mutateString(self.node.inference, Brain.Fuzz.kInferenceValues)
			mutatePoints = True
		else:
			mutatePoints = self.shouldMutate(self._geno.listMutationRate)
		if mutatePoints:
			self.node.inferencePoints = self.mutateFloatList(Brain.Fuzz.kInferenceNum[self.node.inference],
															  self.node.inferencePoints)
	def mutateInterpolation(self):
		''' Interpolation (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.interpolation = self.mutateString(self.node.interpolation, Brain.Fuzz.kInterpolationValues)

	def mutateWrap(self):
		''' Wrap (bool)'''
		if self.shouldMutate(self._geno.boolMutationRate):
			self.node.wrap = not self.node.wrap

	def flipInputs(self):
		''' No alt-inputs allows, so no mutations will occur.
		'''
		pass

###############################################################################
# Noise
###############################################################################
class Noise(Node):
	def __init__(self, genotype, node):
		super(Noise, self).__init__(genotype, node)

	def mutateParameters(self):
		self.mutateRate()
		
	def mutateRate(self):
		''' Rate (float)'''
		if self.shouldMutate(self._geno.floatMutationRate):
			self.node.rate = self.mutateFloat(self.node.rate)

	def flipInputs(self):
		''' No alt-inputs allows, so no mutations will occur.
		'''
		pass
	
###############################################################################
# Timer
###############################################################################
class Timer(Node):
	def __init__(self, genotype, node):
		super(Timer, self).__init__(genotype, node)

	def mutateParameters(self):
		self.mutateRate()
		self.mutateTrigger()
		self.mutateRange()
		self.mutateEndless()
		
	def mutateRate(self):
		''' Rate (float)'''
		if self.shouldMutate(self._geno.floatMutationRate):
			self.node.rate = self.mutateFloat(self.node.rate)

	def mutateTrigger(self):
		''' Trigger (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.trigger = self.mutateString(self.node.trigger, Brain.Timer.kTriggerValues)

	def mutateRange(self):
		''' Range (float, float)'''
		if self.shouldMutate(self._geno.rangeMutationRate):
			self.node.range = self.mutateFloatRange(self.node.range)

	def mutateEndless(self):
		''' Endless (bool)'''
		if self.shouldMutate(self._geno.boolMutationRate):
			self.node.endless = not self.node.endless

	def flipInputs(self):
		''' One alt and one regular input allowed.
		'''
		if (self.node.inputs or self.node.altInputs):
			if self.shouldMutate(self._geno.flipInputRate):
				if self.node.inputs and self.node.altInputs:
					temp = self.node.inputs.pop()
					self.node.inputs.append(self.node.altInputs.pop())
					self.node.altInputs.append(temp)
				elif not self.node.altInputs:
					self.node.altInputs.append(self.node.inputs.pop())
				else:
					self.node.inputs.append(self.node.altInputs.pop())

###############################################################################
# Input
###############################################################################
class Input(Node):
	def __init__(self, genotype, node):
		super(Input, self).__init__(genotype, node)

	def mutateParameters(self):
		self.mutateValue()
		self.mutateIntegrate()
		self.mutateRange()
		
	def mutateValue(self):
		''' Mutate either the Channel (string) or the Output (float)
			If the channel is set and it should mutate, switch to
			output for some percentage of the time. And vice versa.'''
		if self.node.channel:
			if self.shouldMutate(self._geno.stringMutationRate):
				if self.shouldMutate(self._geno.switchInputRate):
					self.node.channel = ""
					self.node.output = self.mutateFloat(self.node.output)
				else:
					self.node.channel = self.mutateString(self.node.channel, self._geno.inputChannels())
		elif self.shouldMutate(self._geno.floatMutationRate):
			if self.shouldMutate(self._geno.switchInputRate):
				self.node.channel = self.mutateString(self.node.channel, self._geno.inputChannels())
			else:
				self.node.output = self.mutateFloat(self.node.output)

	def mutateIntegrate(self):
		''' Integrate (string)'''
		if self.shouldMutate(self._geno.stringMutationRate):
			self.node.integrate = self.mutateString(self.node.integrate, Brain.Input.kIntegrateValues)

	def mutateRange(self):
		''' Range (float, float)'''
		if self.shouldMutate(self._geno.rangeMutationRate):
			self.node.range = self.mutateFloatRange(self.node.range)

	def flipInputs(self):
		''' No alt-inputs allows, so no mutations will occur.
		'''
		pass
