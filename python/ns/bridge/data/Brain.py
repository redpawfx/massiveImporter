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
		self.__id = 0
		self.__idSet = False
		self.__name = ""
		self.__nameSet = False
		self.__translate = []
		self.__translateSet = False
		self.__inputs = []
		self.__inputsSet = False
		self.__altInputs = []
		self.__altInputsSet = False
		self.__parent = 0
		self.__parentSet = False

	def __setId(self, val):
		self.__id = val
		self.__idSet = True
	def __getId(self): return self.__id
	id = property(__getId, __setId)
	
	def __setName(self, val):
		self.__name = val
		self.__nameSet = True
	def __getName(self): return self.__name
	name = property(__getName, __setName)
	
	def __setTranslate(self, val):
		self.__translate = val
		self.__translateSet = True
	def __getTranslate(self): return self.__translate
	translate = property(__getTranslate, __setTranslate)
	
	def __setInputs(self, val):
		self.__inputs = val
		self.__inputsSet = True
	def __getInputs(self): return self.__inputs
	inputs = property(__getInputs, __setInputs)
	
	def __setAltInputs(self, val):
		self.__altInputs = val
		self.__altInputsSet = True
	def __getAltInputs(self): return self.__altInputs
	altInputs = property(__getAltInputs, __setAltInputs)
	
	def __setParent(self, val):
		self.__parent = val
		self.__parentSet = True
	def __getParent(self): return self.__parent
	parent = property(__getParent, __setParent)

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
		if self.__idSet:
			fileHandle.write("    id        %d\n" % self.id)
		if self.__nameSet:
			fileHandle.write("    name      %s\n" % self.name)
		if self.__translateSet:
			fileHandle.write("    translate %d %d\n" % (self.translate[0], self.translate[1]))
		
	def _dumpFooter(self, fileHandle):
		if self.__inputsSet:
			if len(self.inputs) == 1:
				fileHandle.write("    %d input" % len(self.inputs))
			else:
				fileHandle.write("    %d inputs" % len(self.inputs))
			for input in self.inputs:
				fileHandle.write(" %d" % input)
			fileHandle.write("\n")
		if self.__altInputsSet:
			if len(self.altInputs) == 1:
				fileHandle.write("    %d alt input" % len(self.altInputs))
			else:
				fileHandle.write("    %d alt inputs" % len(self.altInputs))
			for input in self.altInputs:
				fileHandle.write(" %d" % input)
			fileHandle.write("\n")
		if self.__parentSet:
			fileHandle.write("    parent %d\n" % self.parent)

class Input(Node):
	def __init__(self):
		super(Input, self).__init__()
		self.__channel = ""
		self.__channelSet = False
		self.__integrate = ""
		self.__integrateSet = False
		self.__range = []
		self.__rangeSet = False
		self.__output = 0
		self.__outputSet = False
		
	def __setChannel(self, val):
		self.__channel = val
		self.__channelSet = True
	def __getChannel(self): return self.__channel
	channel = property(__getChannel, __setChannel)

	def __setIntegrate(self, val):
		self.__integrate = val
		self.__integrateSet = True
	def __getIntegrate(self): return self.__integrate
	integrate = property(__getIntegrate, __setIntegrate)

	def __setRange(self, val):
		self.__range = val
		self.__rangeSet = True
	def __getRange(self): return self.__range
	range = property(__getRange, __setRange)

	def __setOutput(self, val):
		self.__output = val
		self.__outputSet = True
	def __getOutput(self): return self.__output
	output = property(__getOutput, __setOutput)

		
	def _parseTokens(self, tokens):
		if tokens[0] == "channel":
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
		if self.__channelSet:
			fileHandle.write("    channel %s\n" % self.channel)
		if self.__outputSet:
			fileHandle.write("    output  %f\n" % self.output)
		if self.__integrateSet:
			fileHandle.write("    integrate %s\n" % self.integrate)
		if self.__rangeSet:
			fileHandle.write("    range %f %f\n" % (self.range[0], self.range[1]))
		self._dumpFooter(fileHandle)
		
class Output(Node):
	def __init__(self):
		super(Output, self).__init__()
		self.__channel = ""
		self.__channelSet = False
		self.__defuzz = ""
		self.__defuzzSet = False
		self.__integrate = ""
		self.__integrateSet = False
		self.__range = []
		self.__rangeSet = False
		self.__delay = 0.0
		self.__delaySet = False
		self.__rate = 0.0
		self.__rateSet = False
		self.__output = 0.0
		self.__outputSet = False
		self.__manual = False
		
	def __setChannel(self, val):
		self.__channel = val
		self.__channelSet = True
	def __getChannel(self): return self.__channel
	channel = property(__getChannel, __setChannel)
	
	def __setDefuzz(self, val):
		self.__defuzz = val
		self.__defuzzSet = True
	def __getDefuzz(self): return self.__defuzz
	defuzz = property(__getDefuzz, __setDefuzz)
	
	def __setIntegrate(self, val):
		self.__integrate = val
		self.__integrateSet = True
	def __getIntegrate(self): return self.__integrate
	integrate = property(__getIntegrate, __setIntegrate)
	
	def __setRange(self, val):
		self.__range = val
		self.__rangeSet = True
	def __getRange(self): return self.__range
	range = property(__getRange, __setRange)
	
	def __setDelay(self, val):
		self.__delay = val
		self.__delaySet = True
	def __getDelay(self): return self.__delay
	delay = property(__getDelay, __setDelay)
	
	def __setRate(self, val):
		self.__rate = val
		self.__rateSet = True
	def __getRate(self): return self.__rate
	rate = property(__getRate, __setRate)
	
	def __setOutput(self, val):
		self.__output = val
		self.__outputSet = True
	def __getOutput(self): return self.__output
	output = property(__getOutput, __setOutput)
	
	def __setManual(self, val):
		self.__manual = val
	def __getManual(self): return self.__manual
	manual = property(__getManual, __setManual)

		
	def _parseTokens(self, tokens):
		'''	If Manual is enabled the output value is stored in the 'output'
			token.'''
		if tokens[0] == "channel":
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
		if self.__channelSet:
			fileHandle.write("    channel %s\n" % self.channel)
		if self.__outputSet:
			fileHandle.write("    output  %f\n" % self.output)
		if self.__manual:
			fileHandle.write("    manual\n")
		if self.__defuzzSet:
			fileHandle.write("    defuzz  %s\n" % self.defuzz)
		if self.__integrateSet:
			fileHandle.write("    integrate %s\n" % self.integrate)
		if self.__rangeSet:
			fileHandle.write("    range %f %f\n" % (self.range[0], self.range[1]))
		if self.__delaySet:
			fileHandle.write("    delay %f\n" % self.delay)
		if self.__rateSet:
			fileHandle.write("    rate %f\n" % self.rate)
		self._dumpFooter(fileHandle)
				
class Fuzz(Node):
	def __init__(self):
		super(Fuzz, self).__init__()
		self.__inference = ""
		self.__inferenceSet = False
		self.__inferencePoints = []
		self.__interpolation = ""
		self.__interpolationSet = False
		self.__wrap = False

	def __setInference(self, val):
		self.__inference = val
		self.__inferenceSet = True
	def __getInference(self): return self.__inference
	inference = property(__getInference, __setInference)

	def __setInferencePoints(self, val):
		self.__inferencePoints = val
	def __getInferencePoints(self): return self.__inferencePoints
	inferencePoints = property(__getInferencePoints, __setInferencePoints)

	def __setInterpolation(self, val):
		self.__interpolation = val
		self.__interpolationSet = True
	def __getInterpolation(self): return self.__interpolation
	interpolation = property(__getInterpolation, __setInterpolation)

	def __setWrap(self, val):
		self.__wrap = val
	def __getWrap(self): return self.__wrap
	wrap = property(__getWrap, __setWrap)


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
		if self.__inferenceSet:
			fileHandle.write("    %s inference" % self.inference)
			for point in self.inferencePoints:
				fileHandle.write(" %f" % point)
			fileHandle.write("\n")
		if self.__interpolationSet:
			fileHandle.write("    %s interpolation\n" % self.interpolation)
		if self.__wrap:
			fileHandle.write("    wrap\n")
		self._dumpFooter(fileHandle)
		
		
class Rule(Node):
	def __init__(self):
		super(Rule, self).__init__()
		self.__weight = 0.0
		self.__weightSet = False
		self.__type = "min"
		self.__typeSet = False

	def __setWeight(self, val):
		self.__weight = val
		self.__weightSet = True
	def __getWeight(self): return self.__weight
	weight = property(__getWeight, __setWeight)
	
	def __setType(self, val):
		self.__type = val
		self.__typeSet = True
	def __getType(self): return self.__type
	type = property(__getType, __setType)
	
	def _parseTokens(self, tokens):
		if tokens[0] == "weight":
			self.weight = float(tokens[1])	
		elif tokens[0] == "and":
			self.type = tokens[1]	

	def dump(self, fileHandle):
		fileHandle.write("fuzzy rule\n")
		self._dumpHeader(fileHandle)
		if self.__weightSet:
			fileHandle.write("    weight  %f\n" % self.weight)
		if self.__typeSet:
			fileHandle.write("    and     %s\n" % self.type)
		self._dumpFooter(fileHandle)

class Or(Node):
	def __init__(self):
		super(Or, self).__init__()
		self.__weight = 0.0
		self.__weightSet = False
		self.__type = "max"
		self.__typeSet = False

	def __setWeight(self, val):
		self.__weight = val
		self.__weightSet = True
	def __getWeight(self): return self.__weight
	weight = property(__getWeight, __setWeight)
	
	def __setType(self, val):
		self.__type = val
		self.__typeSet = True
	def __getType(self): return self.__type
	type = property(__getType, __setType)
		
	def _parseTokens(self, tokens):
		if tokens[0] == "weight":
			self.weight = float(tokens[1])	
		elif tokens[0] == "or":
			self.type = tokens[1]	

	def dump(self, fileHandle):
		fileHandle.write("fuzzy or\n")
		self._dumpHeader(fileHandle)
		if self.__weightSet:
			fileHandle.write("    weight  %f\n" % self.weight)
		if self.__typeSet:
			fileHandle.write("    or %s\n" % self.type)
		self._dumpFooter(fileHandle)
		
class Defuzz(Node):
	def __init__(self):
		super(Defuzz, self).__init__()
		self.__defuzz = 0.0
		self.__defuzzSet = False
		self.__isElse = False

	def __setDefuzz(self, val):
		self.__defuzz = val
		self.__defuzzSet = True
	def __getDefuzz(self): return self.__defuzz
	defuzz = property(__getDefuzz, __setDefuzz)
	
	def __setIsElse(self, val):
		self.__isElse = val
	def __getIsElse(self): return self.__isElse
	isElse = property(__getIsElse, __setIsElse)

	def _parseTokens(self, tokens):
		if tokens[0] == "defuzz":
			self.defuzz = float(tokens[1])
		elif tokens[0] == "else":
			self.isElse = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy defuzz\n")
		self._dumpHeader(fileHandle)
		if self.__defuzzSet:
			fileHandle.write("    defuzz  %f\n" % self.defuzz)
		if self.__isElse:
			fileHandle.write("    else\n")
		self._dumpFooter(fileHandle)

class Noise(Node):
	def __init__(self):
		super(Noise, self).__init__()
		self.__rate = 0
		self.__rateSet = False
		self.__seed = 0
		self.__seedSet = False
		self.__output = 0.0
		self.__outputSet = False

	def __setRate(self, val):
		self.__rate = val
		self.__rateSet = True
	def __getRate(self): return self.__rate
	rate = property(__getRate, __setRate)
	
	def __setSeed(self, val):
		self.__seed = val
		self.__seedSet = True
	def __getSeed(self): return self.__seed
	seed = property(__getSeed, __setSeed)

	def __setOutput(self, val):
		self.__output = val
		self.__outputSet = True
	def __getOutput(self): return self.__output
	output = property(__getOutput, __setOutput)
	
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
		if self.__rateSet:
			fileHandle.write("    rate    %s\n" % formatFloat(self.rate))
		if self.__seedSet:
			fileHandle.write("    seed    %d\n" % self.seed)
		if self.__outputSet:
			fileHandle.write("    output  %s\n" % formatFloat(self.output))
		self._dumpFooter(fileHandle)
				
class Timer(Node):
	def __init__(self):
		super(Timer, self).__init__()
		self.__rate = 0
		self.__rateSet = False
		self.__trigger = ""
		self.__triggerSet= False
		self.__range = [0.0, 1.0]
		self.__rangeSet = False
		self.__endless = False

	def __setRate(self, val):
		self.__rate = val
		self.__rateSet = True
	def __getRate(self): return self.__rate
	rate = property(__getRate, __setRate)
	
	def __setTrigger(self, val):
		self.__trigger = val
		self.__triggerSet = True
	def __getTrigger(self): return self.__trigger
	trigger = property(__getTrigger, __setTrigger)
	
	def __setRange(self, val):
		self.__range = val
		self.__rangeSet = True
	def __getRange(self): return self.__range
	range = property(__getRange, __setRange)
	
	def __setEndless(self, val):
		self.__endless = val
	def __getEndless(self): return self.__endless
	endless = property(__getEndless, __setEndless)
	
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
		if self.__rateSet:
			fileHandle.write("    rate    %s\n" % formatFloat(self.rate))
		if self.__triggerSet:
			fileHandle.write("    trigger %s\n" % self.trigger)
		if self.__rangeSet:
			fileHandle.write("    range %s %s\n" % (formatFloat(self.range[0]), formatFloat(self.range[1])))
		if self.__endless:
			fileHandle.write("    endless\n")
		self._dumpFooter(fileHandle)

class Macro(Node):
	def __init__(self):
		super(Macro, self).__init__()
		self.__child = 0
		self.__childSet = False
		
	def __setChild(self, val):
		self.__child = val
		self.__childSet = True
	def __getChild(self): return self.__child
	child = property(__getChild, __setChild)
		
	def _parseTokens(self, tokens):
		if tokens[0] == "child":
			self.child = int(tokens[1])			

	def dump(self, fileHandle):
		fileHandle.write("fuzzy macro\n")
		self._dumpHeader(fileHandle)
		if self.__childSet:
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
