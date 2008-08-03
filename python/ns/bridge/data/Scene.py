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
import os.path

import ns.bridge.data.MasSpec as MasSpec
import ns.bridge.io.MasReader as MasReader
import ns.bridge.io.CDLReader as CDLReader

class Scene:
	'''Load files and collect description data related to a Massive Scene.
	   This includes .mas, .cdl  and related files. This does not include sim
	   data such as callsheets and simmed .apf or .amc files.'''
	def __init__(self):
		self._mas = MasSpec.MasSpec()
		self._agentSpecMap = {}
		self._agentSpecs = []
		self_baseName = ""
		
	def resolvePath(self, path):
		'''If path is not absolute, assume it is relative to the root path
		   directory.'''
		resolved = path
		if self._mas.rootPath() and not os.path.isabs(resolved):
			resolved = "%s/%s" % (self._mas.rootPath(), path)
		return resolved
	
	def baseName(self):
		'''.mas file name without the extension.'''
		return self._baseName
	
	def agentSpecs(self):
		return self._agentSpecs
	
	def mas(self):
		return self._mas
	
	def setMas(self, masFile):
		'''Load a .mas file into a MasSpec, and any referenced .cdl files into
		   AgentSpecs.'''
		  
		self._baseName = os.path.splitext(os.path.basename(masFile))[0]
		self._mas = MasReader.read(masFile)
		
		for cdlFile in self._mas.cdlFiles:
			self.addCdl(cdlFile.file, cdlFile.type)
			
	def addCdl(self, cdlFile, type=""):
		path = self.resolvePath(cdlFile)
		self.agentSpec(path, type)
			
	def agentSpec(self, key, type = ""):
		'''Key is either an agent type or the absolute path to a CDL file.'''
		agentSpec = None
		try:
			agentSpec = self._agentSpecMap[key]
		except:
			if os.path.isfile(key):
				agentSpec = CDLReader.read(key)
				if type:
					# By default an agent's type will be determined by the
					# object keyword in the CDL file. However if the agent is
					# being loaded as part of a Massive Scene, the agent type
					# will be determined by the group keyword in the MAS file.
					# This prevents agent type name clashes as the MAS file
					# agent type includes an id unique within the Massive
					# scene.
					#
					agentSpec.agentType = type
				# Hash the Spec twice. If a callsheet is not provided
				# the importer will use the agent names found in the sim data
				# as the agent types
				#
				self._agentSpecMap[agentSpec.cdlFile] = agentSpec
				self._agentSpecMap[agentSpec.agentType] = agentSpec
				self._agentSpecs.append( agentSpec )
			else:
				raise
		return agentSpec
	