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
import os.path

	
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

class CdlFile:
	def __init__(self, file, type=""):
		self.file = file
		self.type = type

class MasDescription:
	def __init__(self):
		self.path = ""
		self.masFile = ""
		self.cdlFiles = []
		self.terrainFile = ""
		self.selectionGroup = SelectionGroup()
		self.numAgents = 0

def _handleTerrain( fileHandle, tokens, mas ):
	'''Load terrain information. For now only the terrain OBJ file is loaded'''
	for line in fileHandle:
		line = line.strip()
		if line == "End terrain":
			# End of terrain section. Parsing engine expects tokens for the
			# next line though, so get 'em and return
			#
			tokens = []
			try:
				tokens = fileHandle.next().strip.split()
			except:
				pass
			return tokens
		
		tokens = line.split()
		if tokens:
			if tokens[0] == "model":
				assert len(tokens) == 2
				mas.terrainFile = tokens[1]
			else:
				# skip the other tags for now
				pass
	return []

def _handlePlace( fileHandle, tokens, mas ):
	'''Load placement information. For now we only care about the CDL files.'''
	for line in fileHandle:
		line = line.strip()
		if line == "End place":
			# End of Place section. Parsing engine expects tokens for the
			# next line though, so get 'em and return
			#
			tokens = []
			try:
				tokens = fileHandle.next().strip.split()
			except:
				pass
			return tokens
				
		tokens = line.split()
		if tokens:
			if tokens[0] == "group":
				# ignore everything but CDL files.
				# Here's hoping that group statements only contain 3 lines
				# otherwise I gotta start looking at whitespace to figure
				# out when the group statement is done
				#
				agentType = tokens[2]
				for i in range(3):
					tokens = fileHandle.next().strip().split()
					if tokens[0] == "cdl":
						mas.cdlFiles.append( CdlFile( tokens[1], agentType ) )
			elif tokens[0] == "selection":
				if len(tokens) != 2:
					continue
				name = tokens[1]
				selection = Selection()
				line = fileHandle.next().strip()
				while line != "end selection":
					tokens = line.split()
					if not tokens:
						continue
					selection.addRanges(tokens)
					line = fileHandle.next().strip()
				mas.selectionGroup.addSelection( name, selection )
			elif tokens[0] == "generator":
				line = fileHandle.next().strip()
				while line != "end generator":
					tokens = line.split()
					if not tokens:
						continue
					if tokens[0] == "number":
						mas.numAgents += int(tokens[1])
					line = fileHandle.next().strip()
			else:
				# skip the other tags for now
				pass
	return []

def read(fullName):
	'''Load information about the Massive setup'''
 
	mas = MasDescription()
	(mas.path, mas.masFile) = os.path.split(fullName)

	fileHandle = open(fullName, "r")
 	
 	try:
		for line in fileHandle:
			tokens = line.strip().split()
	 		if tokens:
	 			if tokens[0] == "Terrain":
	 				tokens = _handleTerrain( fileHandle, tokens, mas )
	 			elif tokens[0] == "Place":
	 				tokens = _handlePlace( fileHandle, tokens, mas )
	 			else:
	 				pass
	except:
	 	fileHandle.close()
	 	print >> sys.stderr, "Error reading MAS file %s" % fullName
	 	raise
	 	
	fileHandle.close()
 	return mas
 

        
