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

def formatFloat(flt):
	# Remove any trailing 0's. If that leaves just a period, remove it too. We
	# can't strip both at once otherwise '0.000' becomes '' and we want '0'
	return str(flt).rstrip('0').rstrip('.')

class Node(object):
	def __init__(self):
		self._id = 0
		self._idSet = False
		self._name = ""
		self._nameSet = False
		self._translate = []
		self._translateSet = False
		self._inputs = []
		self._inputsSet = False
		self._altInputs = []
		self._altInputsSet = False
		self._parent = 0
		self._parentSet = False

	def _setId(self, val):
		self._id = val
		self._idSet = True
	def _getId(self): return self._id
	id = property(_getId, _setId)
	
	def _setName(self, val):
		self._name = val
		self._nameSet = True
	def _getName(self): return self._name
	name = property(_getName, _setName)
	
	def _setTranslate(self, val):
		self._translate = val
		self._translateSet = True
	def _getTranslate(self): return self._translate
	translate = property(_getTranslate, _setTranslate)
	
	def _setInputs(self, val):
		self._inputs = val
		self._inputsSet = True
	def _getInputs(self): return self._inputs
	inputs = property(_getInputs, _setInputs)
	
	def _setAltInputs(self, val):
		self._altInputs = val
		self._altInputsSet = True
	def _getAltInputs(self): return self._altInputs
	altInputs = property(_getAltInputs, _setAltInputs)
	
	def _setParent(self, val):
		self._parent = val
		self._parentSet = True
	def _getParent(self): return self._parent
	parent = property(_getParent, _setParent)

	def load(self, fileHandle):
		line = ""
		for line in fileHandle:
			tokens = line.strip().split()
			if not line[0].isspace():
				break
			if tokens:
				if tokens[0] == "id":
					self.id = int(tokens[1])
				elif tokens[0] == "name":
					self.name = " ".join(tokens[1:])
				elif tokens[0] == "translate":
					self.translate = [ int(tokens[1]), int(tokens[2]) ]	
				elif tokens[0] == "parent":
					self.parent = int(tokens[1])	
				elif len(tokens) > 2 and (tokens[1] == "inputs" or tokens[1] == "input"):
					self.inputs = [ int(input) for input in tokens[2:] ]	
				elif len(tokens) > 3 and tokens[1] == "alt" and (tokens[2] == "inputs" or tokens[2] == "input"):
					self.altInputs = [ int(input) for input in tokens[3:] ]
				else:
					self._parseTokens(tokens)
			
		return line
	
	def _dumpHeader(self, fileHandle):
		if self._idSet:
			fileHandle.write("    id        %d\n" % self.id)
		if self._nameSet:
			fileHandle.write("    name      %s\n" % self.name)
		if self._translateSet:
			fileHandle.write("    translate %d %d\n" % (self.translate[0], self.translate[1]))
		
	def _dumpFooter(self, fileHandle):
		if self._inputsSet:
			if len(self.inputs) == 1:
				fileHandle.write("    %d input" % len(self.inputs))
			else:
				fileHandle.write("    %d inputs" % len(self.inputs))
			for input in self.inputs:
				fileHandle.write(" %d" % input)
			fileHandle.write("\n")
		if self._altInputsSet:
			if len(self.altInputs) == 1:
				fileHandle.write("    %d alt input" % len(self.altInputs))
			else:
				fileHandle.write("    %d alt inputs" % len(self.altInputs))
			for input in self.altInputs:
				fileHandle.write(" %d" % input)
			fileHandle.write("\n")
		if self._parentSet:
			fileHandle.write("    parent %d\n" % self.parent)

class Input(Node):
	def __init__(self):
		super(Input, self).__init__()
		self._channel = ""
		self._channelSet = False
		self._integrate = ""
		self._integrateSet = False
		self._range = []
		self._rangeSet = False
		self._output = 0
		self._outputSet = False
		
	def _setChannel(self, val):
		self._channel = val
		self._channelSet = True
	def _getChannel(self): return self._channel
	channel = property(_getChannel, _setChannel)

	def _setIntegrate(self, val):
		self._integrate = val
		self._integrateSet = True
	def _getIntegrate(self): return self._integrate
	integrate = property(_getIntegrate, _setIntegrate)

	def _setRange(self, val):
		self._range = val
		self._rangeSet = True
	def _getRange(self): return self._range
	range = property(_getRange, _setRange)

	def _setOutput(self, val):
		self._output = val
		self._outputSet = True
	def _getOutput(self): return self._output
	output = property(_getOutput, _setOutput)

		
	def _parseTokens(self, tokens):
		if tokens[0] == "channel":
			if len(tokens) > 1:
				self.channel = tokens[1]	
		elif tokens[0] == "integrate":
			self.integrate = tokens[1]	
		elif tokens[0] == "range":
			self.range = [ float(tokens[1]), float(tokens[2]) ]	
		elif tokens[0] == "output":
			self.output = float(tokens[1])

	def dump(self, fileHandle):
		fileHandle.write("fuzzy input\n")
		self._dumpHeader(fileHandle)
		if self._channelSet:
			fileHandle.write("    channel %s\n" % self.channel)
		if self._outputSet:
			fileHandle.write("    output  %f\n" % self.output)
		if self._integrateSet:
			fileHandle.write("    integrate %s\n" % self.integrate)
		if self._rangeSet:
			fileHandle.write("    range %f %f\n" % (self.range[0], self.range[1]))
		self._dumpFooter(fileHandle)
		
class Output(Node):
	kIntegrateValues = ["position", "speed"]
	kDefuzzValues = ["COM", "MOM", "BLEND"]
	
	def __init__(self):
		super(Output, self).__init__()
		self._channel = ""
		self._channelSet = False
		self._defuzz = ""
		self._defuzzSet = False
		self._integrate = ""
		self._integrateSet = False
		self._range = []
		self._rangeSet = False
		self._delay = 0.0
		self._delaySet = False
		self._rate = 0.0
		self._rateSet = False
		self._output = 0.0
		self._outputSet = False
		self._manual = False
		
	def _setChannel(self, val):
		self._channel = val
		self._channelSet = True
	def _getChannel(self): return self._channel
	channel = property(_getChannel, _setChannel)
	
	def _setDefuzz(self, val):
		self._defuzz = val
		self._defuzzSet = True
	def _getDefuzz(self): return self._defuzz
	defuzz = property(_getDefuzz, _setDefuzz)
	
	def _setIntegrate(self, val):
		self._integrate = val
		self._integrateSet = True
	def _getIntegrate(self): return self._integrate
	integrate = property(_getIntegrate, _setIntegrate)
	
	def _setRange(self, val):
		self._range = val
		self._rangeSet = True
	def _getRange(self): return self._range
	range = property(_getRange, _setRange)
	
	def _setDelay(self, val):
		self._delay = val
		self._delaySet = True
	def _getDelay(self): return self._delay
	delay = property(_getDelay, _setDelay)
	
	def _setRate(self, val):
		self._rate = val
		self._rateSet = True
	def _getRate(self): return self._rate
	rate = property(_getRate, _setRate)
	
	def _setOutput(self, val):
		self._output = val
		self._outputSet = True
	def _getOutput(self): return self._output
	output = property(_getOutput, _setOutput)
	
	def _setManual(self, val):
		self._manual = val
	def _getManual(self): return self._manual
	manual = property(_getManual, _setManual)

		
	def _parseTokens(self, tokens):
		'''	If Manual is enabled the output value is stored in the 'output'
			token.'''
		if tokens[0] == "channel":
			if len(tokens) > 1:
				self.channel = tokens[1]	
		elif tokens[0] == "defuzz":
			self.defuzz = tokens[1]
		elif tokens[0] == "integrate":
			self.integrate = tokens[1]	
		elif tokens[0] == "range":
			self.range = [ float(tokens[1]), float(tokens[2]) ]	
		elif tokens[0] == "delay":
			self.delay = float(tokens[1])	
		elif tokens[0] == "rate":
			self.rate = float(tokens[1])	
		elif tokens[0] == "output":
			self.output = float(tokens[1])
		elif tokens[0] == "manual":
			self.manual = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy output\n")
		self._dumpHeader(fileHandle)
		if self._channelSet:
			fileHandle.write("    channel %s\n" % self.channel)
		if self._outputSet:
			fileHandle.write("    output  %f\n" % self.output)
		if self._manual:
			fileHandle.write("    manual\n")
		if self._defuzzSet:
			fileHandle.write("    defuzz  %s\n" % self.defuzz)
		if self._integrateSet:
			fileHandle.write("    integrate %s\n" % self.integrate)
		if self._rangeSet:
			fileHandle.write("    range %f %f\n" % (self.range[0], self.range[1]))
		if self._delaySet:
			fileHandle.write("    delay %f\n" % self.delay)
		if self._rateSet:
			fileHandle.write("    rate %f\n" % self.rate)
		self._dumpFooter(fileHandle)
				
class Fuzz(Node):
	def __init__(self):
		super(Fuzz, self).__init__()
		self._inference = ""
		self._inferenceSet = False
		self._inferencePoints = []
		self._interpolation = ""
		self._interpolationSet = False
		self._wrap = False

	def _setInference(self, val):
		self._inference = val
		self._inferenceSet = True
	def _getInference(self): return self._inference
	inference = property(_getInference, _setInference)

	def _setInferencePoints(self, val):
		self._inferencePoints = val
	def _getInferencePoints(self): return self._inferencePoints
	inferencePoints = property(_getInferencePoints, _setInferencePoints)

	def _setInterpolation(self, val):
		self._interpolation = val
		self._interpolationSet = True
	def _getInterpolation(self): return self._interpolation
	interpolation = property(_getInterpolation, _setInterpolation)

	def _setWrap(self, val):
		self._wrap = val
	def _getWrap(self): return self._wrap
	wrap = property(_getWrap, _setWrap)


	def _parseTokens(self, tokens):
		if tokens[0] == "wrap":
			self.wrap = True
		elif len(tokens) > 1 and tokens[1] == "interpolation":
			self.interpolation = tokens[0]
		elif len(tokens) > 2 and tokens[1] == "inference":
			self.inference = tokens[0]
			self.inferencePoints = [ float(pt) for pt in tokens[2:] ] 				

	def dump(self, fileHandle):
		fileHandle.write("fuzzy fuzz\n")
		self._dumpHeader(fileHandle)
		if self._inferenceSet:
			fileHandle.write("    %s inference" % self.inference)
			for point in self.inferencePoints:
				fileHandle.write(" %f" % point)
			fileHandle.write("\n")
		if self._interpolationSet:
			fileHandle.write("    %s interpolation\n" % self.interpolation)
		if self._wrap:
			fileHandle.write("    wrap\n")
		self._dumpFooter(fileHandle)
		
		
class Rule(Node):
	def __init__(self):
		super(Rule, self).__init__()
		self._weight = 0.0
		self._weightSet = False
		self._type = "min"
		self._typeSet = False

	def _setWeight(self, val):
		self._weight = val
		self._weightSet = True
	def _getWeight(self): return self._weight
	weight = property(_getWeight, _setWeight)
	
	def _setType(self, val):
		self._type = val
		self._typeSet = True
	def _getType(self): return self._type
	type = property(_getType, _setType)
	
	def _parseTokens(self, tokens):
		if tokens[0] == "weight":
			self.weight = float(tokens[1])	
		elif tokens[0] == "and":
			self.type = tokens[1]	

	def dump(self, fileHandle):
		fileHandle.write("fuzzy rule\n")
		self._dumpHeader(fileHandle)
		if self._weightSet:
			fileHandle.write("    weight  %f\n" % self.weight)
		if self._typeSet:
			fileHandle.write("    and     %s\n" % self.type)
		self._dumpFooter(fileHandle)

class Or(Node):
	kTypeValues = ["max", "sum"]
	
	def __init__(self):
		super(Or, self).__init__()
		self._weight = 0.0
		self._weightSet = False
		self._type = "max"
		self._typeSet = False

	def _setWeight(self, val):
		self._weight = val
		self._weightSet = True
	def _getWeight(self): return self._weight
	weight = property(_getWeight, _setWeight)
	
	def _setType(self, val):
		self._type = val
		self._typeSet = True
	def _getType(self): return self._type
	type = property(_getType, _setType)
		
	def _parseTokens(self, tokens):
		if tokens[0] == "weight":
			self.weight = float(tokens[1])	
		elif tokens[0] == "or":
			self.type = tokens[1]	

	def dump(self, fileHandle):
		fileHandle.write("fuzzy or\n")
		self._dumpHeader(fileHandle)
		if self._weightSet:
			fileHandle.write("    weight  %f\n" % self.weight)
		if self._typeSet:
			fileHandle.write("    or %s\n" % self.type)
		self._dumpFooter(fileHandle)
		
class Defuzz(Node):
	def __init__(self):
		super(Defuzz, self).__init__()
		self._defuzz = 0.0
		self._defuzzSet = False
		self._isElse = False

	def _setDefuzz(self, val):
		self._defuzz = val
		self._defuzzSet = True
	def _getDefuzz(self): return self._defuzz
	defuzz = property(_getDefuzz, _setDefuzz)
	
	def _setIsElse(self, val):
		self._isElse = val
	def _getIsElse(self): return self._isElse
	isElse = property(_getIsElse, _setIsElse)

	def _parseTokens(self, tokens):
		if tokens[0] == "defuzz":
			self.defuzz = float(tokens[1])
		elif tokens[0] == "else":
			self.isElse = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy defuzz\n")
		self._dumpHeader(fileHandle)
		if self._defuzzSet:
			fileHandle.write("    defuzz  %f\n" % self.defuzz)
		if self._isElse:
			fileHandle.write("    else\n")
		self._dumpFooter(fileHandle)

class Noise(Node):
	def __init__(self):
		super(Noise, self).__init__()
		self._rate = 0
		self._rateSet = False
		self._seed = 0
		self._seedSet = False
		self._output = 0.0
		self._outputSet = False

	def _setRate(self, val):
		self._rate = val
		self._rateSet = True
	def _getRate(self): return self._rate
	rate = property(_getRate, _setRate)
	
	def _setSeed(self, val):
		self._seed = val
		self._seedSet = True
	def _getSeed(self): return self._seed
	seed = property(_getSeed, _setSeed)

	def _setOutput(self, val):
		self._output = val
		self._outputSet = True
	def _getOutput(self): return self._output
	output = property(_getOutput, _setOutput)
	
	def _parseTokens(self, tokens):
		'''If Manual is checked, the noise value is written as 'output'.'''
		if tokens[0] == "rate":
			self.rate = float(tokens[1])	
		elif tokens[0] == "seed":
			self.seed = int(tokens[1])
		elif tokens[0] == "output":
			self.output = float(tokens[1])

	def dump(self, fileHandle):
		fileHandle.write("fuzzy noise\n")
		self._dumpHeader(fileHandle)
		if self._rateSet:
			fileHandle.write("    rate    %s\n" % formatFloat(self.rate))
		if self._seedSet:
			fileHandle.write("    seed    %d\n" % self.seed)
		if self._outputSet:
			fileHandle.write("    output  %s\n" % formatFloat(self.output))
		self._dumpFooter(fileHandle)
				
class Timer(Node):
	def __init__(self):
		super(Timer, self).__init__()
		self._rate = 0
		self._rateSet = False
		self._trigger = ""
		self._triggerSet= False
		self._range = [0.0, 1.0]
		self._rangeSet = False
		self._endless = False

	def _setRate(self, val):
		self._rate = val
		self._rateSet = True
	def _getRate(self): return self._rate
	rate = property(_getRate, _setRate)
	
	def _setTrigger(self, val):
		self._trigger = val
		self._triggerSet = True
	def _getTrigger(self): return self._trigger
	trigger = property(_getTrigger, _setTrigger)
	
	def _setRange(self, val):
		self._range = val
		self._rangeSet = True
	def _getRange(self): return self._range
	range = property(_getRange, _setRange)
	
	def _setEndless(self, val):
		self._endless = val
	def _getEndless(self): return self._endless
	endless = property(_getEndless, _setEndless)
	
	def _parseTokens(self, tokens):
		if tokens[0] == "rate":
			self.rate = float(tokens[1])	
		elif tokens[0] == "trigger":
			self.trigger = tokens[1]
		elif tokens[0] == "range":
			self.range = [float(tokens[1]), float(tokens[2])]	
		elif tokens[0] == "endless":
			self.endless = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy timer\n")
		self._dumpHeader(fileHandle)
		if self._rateSet:
			fileHandle.write("    rate    %s\n" % formatFloat(self.rate))
		if self._triggerSet:
			fileHandle.write("    trigger %s\n" % self.trigger)
		if self._rangeSet:
			fileHandle.write("    range %s %s\n" % (formatFloat(self.range[0]), formatFloat(self.range[1])))
		if self._endless:
			fileHandle.write("    endless\n")
		self._dumpFooter(fileHandle)

class Macro(Node):
	def __init__(self):
		super(Macro, self).__init__()
		self._child = 0
		self._childSet = False
		
	def _setChild(self, val):
		self._child = val
		self._childSet = True
	def _getChild(self): return self._child
	child = property(_getChild, _setChild)
		
	def _parseTokens(self, tokens):
		if tokens[0] == "child":
			self.child = int(tokens[1])			

	def dump(self, fileHandle):
		fileHandle.write("fuzzy macro\n")
		self._dumpHeader(fileHandle)
		if self._childSet:
			fileHandle.write("    child %d\n" % self.child)
		self._dumpFooter(fileHandle)


class Comment(Node):
	def __init__(self):
		super(Comment, self).__init__()

	def dump(self, fileHandle):
		fileHandle.write("fuzzy commend\n")
		self._dumpHeader(fileHandle)
		self._dumpFooter(fileHandle)
		
class Brain:
	def __init__(self):
		self._nodes = []
		self._ordered = []
		
	def addNode(self, node):
		if node.id >= len(self._nodes):
			self._nodes.extend([0] * (node.id - len(self._nodes) + 1))
		self._nodes[node.id] = node
		self._ordered.append(node)
		
	def nodes(self):
		return self._ordered
	
	def getNode(self, name):
		for node in self._ordered:
			if node.name == name:
				return node
		raise Error("No node named %s" % name)
		
	def loadNode(self, fileHandle, tokens):
		if "input" == tokens[1]:
			node = Input()
		elif "output" == tokens[1]:
			node = Output()
		elif "fuzz" == tokens[1]:
			node = Fuzz()
		elif "defuzz" == tokens[1]:
			node = Defuzz()
		elif "rule" == tokens[1]:
			node = Rule()
		elif "or" == tokens[1]:
			node = Or()
		elif "timer" == tokens[1]:
			node = Timer()
		elif "noise" == tokens[1]:
			node = Noise()
		elif "macro" == tokens[1]:
			node = Macro()
		elif "comment" == tokens[1]:
			node = Comment()
		else:
			raise Exception("Unknown fuzzy node type '%s'." % tokens[1])
		
		line = node.load(fileHandle)
		self.addNode(node)
		
		return line
		
	def dump(self, fileHandle):
		for node in self._ordered:
			node.dump(fileHandle)
