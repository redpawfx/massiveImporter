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

'''Classes to represent Massive selections. These are used to restrict which
   agents will be imported.'''

import sys

class Selection:
	def __init__(self):
		self._ids = set()

	def __repr__(self):
		return `self._ids`
	
	def addRanges( self, ranges ):
		for r in ranges:
			try:
				ids = [ int(r) ]
			except:
				tokens = r.split("-")
				if len(tokens) != 2:
					print >> sys.stderr, "Selection range '%s' not understood. Ignoring." % r
					continue
				try:
					start = int(tokens[0])
					end = int(tokens[1])+1
				except:
					print >> sys.stderr, "Selection range '%s' not understood. Ignoring." % r
					continue					
				ids = range( start, end )
			self._ids.update(ids)
	
	def contains( self, id ):
		return id in self._ids
			
class SelectionGroup:
	def __init__(self):
		self._selections = {}
	
	def __repr__(self):
		s = ""
		for (name, selection) in self._selections.items():
			s += "%s: %s\n" % (name, `selection`)
		return s

	def addSelection(self, name, selection):
		self._selections[name] = selection
		
	def addAnonymousSelection(self, ranges):
		'''Convenience method for adding ranges directly to a SelectionGroup'''
		sel = None
		try:
			sel = self._selections["__anonymous__"]
		except:
			sel = Selection()
			self._selections["__anonymous__"] = sel
		sel.addRanges(ranges)
		
	def selection( self, name ):
		return self._selections[name]
	
	def selectionNames( self ):
		return self._selections.keys()
	
	def contains( self, id ):
		if not self._selections:
			return True
		for selection in self._selections.values():
			if selection.contains( id ):
				return True
		return False
