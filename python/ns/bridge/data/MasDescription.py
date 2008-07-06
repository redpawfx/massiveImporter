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

import ns.bridge.data.Selection as Selection

class CdlFile:
	def __init__(self, file, type=""):
		self.file = file
		self.type = type

class Group:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		
class Locator:
	def __init__(self, groupId, position):
		self.group = groupId
		self.position = tuple(position)

class MasDescription:
	def __init__(self):
		self.path = ""
		self.masFile = ""
		self.cdlFiles = []
		self.terrainFile = ""
		self.groups = []
		self.locators = []
		self.selectionGroup = Selection.SelectionGroup()
		self.numAgents = 0
