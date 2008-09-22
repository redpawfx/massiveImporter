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
import os
import random

class NotRandomValues(object):
	
	def __init__(self):
		self._floatValues = []
		self._intValues = []
		self._floatIndex = 0
		self._intIndex = 0
		self._floatDefault = 0.1
		self._intDefault = 0
		self._floatRandom = True
		self._intRandom = True

	def _setFloatValues(self, val):
		self._floatValues = val
		self._floatIndex = 0
	def _getFloatValues(self): return self._floatValues
	floatValues = property(_getFloatValues, _setFloatValues)

	def _setIntValues(self, val):
		self._intValues = val
		self._intIndex = 0
	def _getIntValues(self): return self._intValues
	intValues = property(_getIntValues, _setIntValues)

	def _setFloatDefault(self, val):
		self._floatDefault = val
		self._floatRandom = False
		self._floatValues = []
	def _getFloatDefault(self): return self._floatDefault
	floatDefault = property(_getFloatDefault, _setFloatDefault)

	def _setIntDefault(self, val):
		self._intDefault = val
		self._intRandom = False
		self._intValues = []
	def _getIntDefault(self): return self._intDefault
	intDefault = property(_getIntDefault, _setIntDefault)
	
	def _setFloatRandom(self, val):
		self._floatRandom = val
		if val: self._floatValues = []
	def _getFloatRandom(self): return self._floatRandom
	floatRandom = property(_getFloatRandom, _setFloatRandom)

	def _setIntRandom(self, val):
		self._intRandom = val
		if val: self._intValues = []
	def _getIntRandom(self): return self._intRandom
	intRandom = property(_getIntRandom, _setIntRandom)

	def randInt(self, a, b):
		if self.intValues and self._intIndex < len(self.intValues):
			val = self._intValues[self._intIndex]
		elif self.intRandom:
			val = random.randint(a, b)
		else:
			val = self.intDefault
		self._intIndex += 1
		return val
	
	def randFloat(self):
		if self.floatValues and self._floatIndex < len(self.floatValues):
			val = self._floatValues[self._floatIndex]	
		elif self.floatRandom:
			val = random.random()
		else:
			val = self.floatDefault
		self._floatIndex += 1
		return val

class NotRandom(object):
	def __init__(self):
		self._default = NotRandomValues()
		self._context = {}
		
	def _getDefault(self): return self._default
	default = property(_getDefault)

	def getContext(self, name):
		try:
			context = self._context[name]
		except:
			self._context[name] = context = NotRandomValues()
		return context
		
	def _getValues(self):
		try:
			outputs = self._context[sys._getframe(2).f_code.co_name]
		except:
			outputs = self.default
		
		return outputs
		
	def random(self):
		return self._getValues().randFloat()
	
	def uniform(self, a, b):
		return self._getValues().randFloat()
	
	def randint(self, a, b):
		return self._getValues().randInt(a, b)
	
	def gauss(self, mu, sigma):
		return self._getValues().randFloat()


	
