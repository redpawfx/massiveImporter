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

class Node:
	def __init__(self):
		self.id = 0
		self.name = ""
		self.translate = []
		self.inputs = []
		self.altInputs = []
		self.parent = 0

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
		fileHandle.write("    id        %d\n" % self.id)
		fileHandle.write("    name      %s\n" % self.name)
		fileHandle.write("    translate %d %d\n" % (self.translate[0], self.translate[1]))
		
	def _dumpFooter(self, fileHandle):
		if self.inputs:
			if len(self.inputs) == 1:
				fileHandle.write("    %d input" % len(self.inputs))
			else:
				fileHandle.write("    %d inputs" % len(self.inputs))
			for input in self.inputs:
				fileHandle.write(" %d" % input)
			fileHandle.write("\n")
		if self.altInputs:
			if len(self.altInputs) == 1:
				fileHandle.write("    %d alt input" % len(self.altInputs))
			else:
				fileHandle.write("    %d alt inputs" % len(self.altInputs))
			for input in self.altInputs:
				fileHandle.write(" %d" % input)
			fileHandle.write("\n")
		if self.parent:
			fileHandle.write("    parent %d\n" % self.parent)

class Input(Node):
	def __init__(self):
		Node.__init__(self)
		self.channel = ""
		self.integrate = ""
		self.range = []
		self.output = 0
		
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
		if self.channel:
			fileHandle.write("    channel %s\n" % self.channel)
		if self.output:
			fileHandle.write("    output  %f\n" % self.output)
		fileHandle.write("    integrate %s\n" % self.integrate)
		fileHandle.write("    range %f %f\n" % (self.range[0], self.range[1]))
		self._dumpFooter(fileHandle)
		
class Output(Node):
	def __init__(self):
		Node.__init__(self)
		self.channel = ""
		self.defuzz = ""
		self.integrate = ""
		self.range = []
		self.delay = 0.0
		self.rate = 0.0
		self.output = 0.0
		self.outputSet = False
		self.manual = False
		
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
			self.outputSet = True
		elif tokens[0] == "manual":
			self.manual = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy output\n")
		self._dumpHeader(fileHandle)
		if self.channel:
			fileHandle.write("    channel %s\n" % self.channel)
		if self.outputSet:
			fileHandle.write("    output  %f\n" % self.output)
		if self.manual:
			fileHandle.write("    manual\n")
		fileHandle.write("    defuzz  %s\n" % self.defuzz)
		fileHandle.write("    integrate %s\n" % self.integrate)
		fileHandle.write("    range %f %f\n" % (self.range[0], self.range[1]))
		if self.delay:
			fileHandle.write("    delay %f\n" % self.delay)
		if self.rate:
			fileHandle.write("    rate %f\n" % self.rate)
		self._dumpFooter(fileHandle)
				
class Fuzz(Node):
	def __init__(self):
		Node.__init__(self)
		self.inference = ""
		self.inferencePoints = []
		self.interpolation = ""
		self.wrap = False

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
		fileHandle.write("    %s inference" % self.inference)
		for point in self.inferencePoints:
			fileHandle.write(" %f" % point)
		fileHandle.write("\n")
		fileHandle.write("    %s interpolation\n" % self.interpolation)
		if self.wrap:
			fileHandle.write("    wrap\n")
		self._dumpFooter(fileHandle)
		
		
class Rule(Node):
	def __init__(self):
		Node.__init__(self)
		self.weight = 0.0
		self.type = "min"
		
	def _parseTokens(self, tokens):
		if tokens[0] == "weight":
			self.weight = float(tokens[1])	
		elif tokens[0] == "and":
			self.type = tokens[1]	

	def dump(self, fileHandle):
		fileHandle.write("fuzzy rule\n")
		self._dumpHeader(fileHandle)
		fileHandle.write("    weight  %f\n" % self.weight)
		fileHandle.write("    and     %s\n" % self.type)
		self._dumpFooter(fileHandle)

class Or(Node):
	def __init__(self):
		Node.__init__(self)
		self.weight = 0.0
		self.type = "max"
		
	def _parseTokens(self, tokens):
		if tokens[0] == "weight":
			self.weight = float(tokens[1])	
		elif tokens[0] == "or":
			self.type = tokens[1]	

	def dump(self, fileHandle):
		fileHandle.write("fuzzy or\n")
		self._dumpHeader(fileHandle)
		fileHandle.write("    weight  %f\n" % self.weight)
		fileHandle.write("    or %s\n" % self.type)
		self._dumpFooter(fileHandle)
		
class Defuzz(Node):
	def __init__(self):
		Node.__init__(self)
		self.defuzz = 0.0
		self.isElse = False

	def _parseTokens(self, tokens):
		if tokens[0] == "defuzz":
			self.defuzz = float(tokens[1])
		elif tokens[0] == "else":
			self.isElse = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy defuzz\n")
		self._dumpHeader(fileHandle)
		fileHandle.write("    defuzz  %f\n" % self.defuzz)
		if self.isElse:
			fileHandle.write("    else\n")
		self._dumpFooter(fileHandle)

class Noise(Node):
	def __init__(self):
		Node.__init__(self)
		self.rate = 0
		self.seed = 0
		self.output = 0.0
		self.manual = False
		
	def _parseTokens(self, tokens):
		'''If Manual is checked, the noise value is written as 'output'.'''
		if tokens[0] == "rate":
			self.rate = float(tokens[1])	
		elif tokens[0] == "seed":
			self.seed = int(tokens[1])
		elif tokens[0] == "output":
			self.output = float(tokens[1])
			self.manual = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy noise\n")
		self._dumpHeader(fileHandle)
		fileHandle.write("    rate    %s\n" % formatFloat(self.rate))
		fileHandle.write("    seed    %d\n" % self.seed)
		if self.manual:
			fileHandle.write("    output  %s\n" % formatFloat(self.output))
		self._dumpFooter(fileHandle)
				
class Timer(Node):
	def __init__(self):
		Node.__init__(self)
		self.rate = 0
		self.trigger = ""
		self._range = []
		self.endless = False
		
	def range(self):
		'''Massive doesn't save the range to disk if it is default.'''
		if self._range:
			return self._range
		else:
			return [0.0, 1.0]
		
	def _parseTokens(self, tokens):
		if tokens[0] == "rate":
			self.rate = float(tokens[1])	
		elif tokens[0] == "trigger":
			self.trigger = tokens[1]
		elif tokens[0] == "range":
			self._range = [float(tokens[1]), float(tokens[2])]	
		elif tokens[0] == "endless":
			self.endless = True

	def dump(self, fileHandle):
		fileHandle.write("fuzzy timer\n")
		self._dumpHeader(fileHandle)
		fileHandle.write("    rate    %s\n" % formatFloat(self.rate))
		fileHandle.write("    trigger %s\n" % self.trigger)
		if self._range:
			fileHandle.write("    range %s %s\n" % (formatFloat(self._range[0]), formatFloat(self._range[1])))
		if self.endless:
			fileHandle.write("    endless\n")
		self._dumpFooter(fileHandle)

class Macro(Node):
	def __init__(self):
		Node.__init__(self)
		self.child = 0
		
	def _parseTokens(self, tokens):
		if tokens[0] == "child":
			self.child = int(tokens[1])			

	def dump(self, fileHandle):
		fileHandle.write("fuzzy macro\n")
		self._dumpHeader(fileHandle)
		fileHandle.write("    child %d\n" % self.child)
		self._dumpFooter(fileHandle)


class Comment(Node):
	def __init__(self):
		Node.__init__(self)

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
