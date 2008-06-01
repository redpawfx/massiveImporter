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

import time

class _Timer:
	def __init__(self):
		self.start = -1.0
		self.elapsed = 0.0

_timers = {}
_timerStack = []
_timerNames = {}

def _timerName(name):
	n = ""
	try:
		n = _timerNames[name]
	except:
		n = name
		if _timerStack:
			prefix = " > ".join( _timerStack )
			n = "%s > %s" % (prefix, name)
	return n

def _pushTimer(name):
	global _timers
	global _timerStack
	global _timerNames
	
	n = _timerName(name)
	_timerStack.append( name )
	_timerNames[name] = n

	timer = None
	try:
		timer = _timers[n]
	except:
		timer = _Timer()
		_timers[n] = timer
	return timer

def _popTimer():
	global _timers
	global _timerStack

	n = _timerName(_timerStack.pop())
	return _timers[n]

def push(name):
	# If the timer was already running this will restart it
	_pushTimer(name).start = time.time()
	
def pop():
	timer = _popTimer()
	if timer.start >= 0:
		timer.elapsed += time.time() - timer.start
		timer.start = -1.0
	return timer.elapsed

def elapsed(name):
	n = _timerName(name)
	return _timers[n].elapsed

def names():
	return _timerNames.values()

def deleteAll():
	global _timers
	global _timerStack
	global _timerNames
	
	_timers = {}
	_timerStack = []
	_timerNames = {}
