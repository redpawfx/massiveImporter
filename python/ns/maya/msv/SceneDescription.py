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

'''Loads Massive specific data from Massive files. This class is later
   passed to the XXXScene class of the appropriate 3rd party software (just
   MayaScene for now), to handle translating the Massive data into something
   that application understands.'''


import sys
import os.path

import ns.py.Timer as Timer

import ns.maya.msv as nmsv
import ns.maya.msv.MasReader as MasReader
import ns.maya.msv.AMCReader as AMCReader
import ns.maya.msv.CDLReader as CDLReader
import ns.maya.msv.SimReader as SimReader
import ns.maya.msv.CallsheetReader as CallsheetReader
import ns.maya.msv.Agent as Agent
import ns.maya.msv.AgentDescription as AgentDescription
import ns.maya.Progress as Progress
import ns.maya.msv.Sim as Sim
import ns.maya.msv.Selection as Selection
from ns.maya.msv.MsvSimLoader import *

class eSkinType:
	smooth, duplicate, instance = range(3)
	
class eAnimType:
	curves, loader = range(2)

class MsvOpt:
	kLoadSkeleton = "loadSkeleton"
	kLoadPrimitives = "loadPrimitives"
	kLoadMaterials = "loadMaterials"
	kLoadGeometry = "loadGeometry"
	kLoadSkin = "loadSkin"
	kLoadActions = "loadActions"
	kMaterialType = "materialType"
	kFrameStep = "frameStep"
	kInstancePrimitives = "instancePrimitives"
	kSkinType = "skinType"
	kSimDir = "simDir"
	kSimType = "simType"
	kMasFile = "masFile"
	kCdlFiles = "cdlFiles"
	kCallsheet = "callsheet"
	kSelections = "selections"
	kCacheGeometry = "cacheGeometry"
	kDeleteSkeleton = "deleteSkeleton"
	kCacheDir = "cacheDir"
	kRange = "range"
	kAnimType = "animType"

class SceneDescription:
	def __init__(self, options):
		self._options = options
		try:
			( self._path, self._masFile ) = os.path.split(options[MsvOpt.kMasFile])
		except:
			self._path = ""
			self._masFile = ""
		
		try:
			self._cdlFiles = [ MasDescription.CdlFile( file ) for file in options[MsvOpt.kCdlFiles] ]
		except:
			self._cdlFiles = []
		
		try:
			self._callsheet = options[MsvOpt.kCallsheet]
		except:
			self._callsheet = ""
		
		try:
			self._simDir = options[MsvOpt.kSimDir]
			if self._simDir[-1] != "/":
				self._simDir += "/"
		except:
			self._simDir = ""
			
		try:
			self.simType = ".%s" % options[MsvOpt.kSimType]
		except:
			self.simType = ".amc"
		
		try:
			self.loadSkeleton = options[MsvOpt.kLoadSkeleton]
		except:
			self.loadSkeleton = True

		try:
			self.loadPrimitives = options[MsvOpt.kLoadPrimitives]
		except:
			self.loadPrimitives = True

		try:
			self.loadMaterials = options[MsvOpt.kLoadMaterials]
		except:
			self.loadMaterials = True

		try:
			self.loadGeometry = options[MsvOpt.kLoadGeometry]
		except:
			self.loadGeometry = True

		try:
			self.loadSkin = options[MsvOpt.kLoadSkin]
		except:
			self.loadSkin = True

		try:
			self.loadActions = options[MsvOpt.kLoadActions]
		except:
			self.loadActions = False
			
		try:
			self.materialType = options[MsvOpt.kMaterialType]
		except:
			self.materialType = "blinn"
		
		try:
			self.frameStep = int(options[MsvOpt.kFrameStep])
		except:
			self.frameStep = 1
			
		try:
			self.instancePrimitives = int(options[MsvOpt.kInstancePrimitives])
		except:
			self.instancePrimitives = 1
		
		try:
			skinTypeString = str(options[MsvOpt.kSkinType])
		except:
			skinTypeString = "smooth"
			
		try:
			self._selectionNames = options[MsvOpt.kSelections]
		except:
			self._selectionNames = []
			
		try:
			self.cacheGeometry = int(options[MsvOpt.kCacheGeometry])
		except:
			self.cacheGeometry = 0

		try:
			self.deleteSkeleton = int(options[MsvOpt.kDeleteSkeleton])
		except:
			self.deleteSkeleton = 0

		try:
			self.cacheDir = options[MsvOpt.kCacheDir]
		except:
			self.cacheDir = ""
			
		try:
			self.range = options[MsvOpt.kRange]
		except:
			self.range = ""
			
		try:
			animTypeString = options[MsvOpt.kAnimType]
		except:
			animTypeString = "curves"
	
		self.skinType = eSkinType.smooth
		if "smooth" == skinTypeString:
			self.skinType = eSkinType.smooth
		elif "instance" == skinTypeString:
			self.skinType = eSkinType.instance
		elif "duplicate" == skinTypeString:
			self.skinType = eSkinType.duplicate

		self.animType = eAnimType.curves
		if "curves" == animTypeString:
			self.animType = eAnimType.curves
		elif "loader" == animTypeString:
			self.animType = eAnimType.loader
		
		self._terrainFile = ""
		
		self._agents = {}
		self._agentDescriptions = {}
		self.perInstanceVariables = {}
		self.sims = {}
		
		self._selectionGroup = Selection.SelectionGroup()
		if self.range:
			tokens = self.range.split()
			sel = Selection.Selection()
			sel.addRanges( tokens )
			self._selectionGroup.addSelection( "NimbleMsv", sel )

	def baseName(self):
		'''MAS file name without the extension.'''
		return os.path.splitext(self._masFile)[0]

	def resolvePath(self, path):
		'''If path is not absolute, assume it is relative to the MAS file
		   directory.'''
		resolved = path
		if not os.path.isabs(resolved):
			resolved = "%s/%s" % (self._path, path)
		return resolved

	def terrainFile(self):
		'''Path to the terrain file.'''
		if self._terrainFile:
			return self.resolvePath( self._terrainFile )
		else:
			return ""
		
	def simDir(self):
		if self._simDir:
			return self.resolvePath( self._simDir )
		else:
			return ""
		
	def agentDesc( self, key, type = "" ):
		'''Key is either an agent type or a CDL file name.'''
		agentDesc = None
		try:
			agentDesc = self._agentDescriptions[key]
		except:
			if os.path.isfile(key):
				cdlReader = CDLReader.CDLReader()
				agentDesc = cdlReader.read( key )
				if type:
					# By default an agent's type will be determined by the
					# object keyword in the CDL file. However if the agent is
					# being loaded as part of a Massive Scene, the agent type
					# will be determined by the group keyword in the MAS file.
					# This prevents agent type name clashes as the MAS file
					# agent type includes an id unique within the Massive
					# scene.
					#
					agentDesc.agentType = type
				# Hash the description twice. If a callsheet is not provided
				# the importer will use the agent names found in the sim data
				# as the agent types
				#
				self._agentDescriptions[agentDesc.cdl] = agentDesc
				self._agentDescriptions[agentDesc.agentType] = agentDesc
			else:
				raise
		return agentDesc		

	def addAgent( self, agentName, agent ):
		self._agents[agentName] = agent
		
	def agentByName( self, agentName ):
		return self._agents[agentName]

	def agentType(self, agentName):
		'''If this agent exists, query its agentType, otherwise try to 
		   guess its agentType by parsing its name. Massive agents are usually
		   named like: agentType_id'''
		agentType = ""
		try:
			agentType = self.agentByName(agentName).agentType
		except:
			agentType = agentName.split("_")[0]
		return agentType
	
	def agentId( self, agentName ):
		'''If this agent exists, query its agent id, otherwise try to 
		   guess its agent id by parsing its name. Massive agents are usually
		   named like: agentType_id'''
		agentId = -1
		try:
			agentId = self.agentByName(agentName).id
		except:
			agentId = int(agentName.split("_")[-1])
		return agentId
		
	def agents( self ):
		return self._agents.values()

	def numAgents( self ):
		return len(self.agents())

	def buildAgent( self, agentName, id = -1, agentDesc = None ):
		'''If the given agent already exists, return it. Otherwise guess
		   its agent type and id based on its name, and build a new agent
		   with the appropriate AgentDesc. If no AgentDesc exists for that
		   type, raise an error. This method also handles filtering out
		   agents that do not exist in the user specified "selections"'''
		
		if id < 0:
			id = self.agentId( agentName )
			
		if not self._selectionGroup.contains( id ):
			# Filter out non-selected agents
			#
			return None
		
		try:
			agent = self.agentByName( agentName )
		except:
			# agentName does not already exist (probably no callsheet was
			# provided) - build one *if* the agentType is defined. The
			# agentType should have already been defined if a CDL file
			# was specified in the MAS file for the agentType.
			#)
			if not agentDesc:
				agentDesc = self.agentDesc( self.agentType( agentName ) )
			
			agent = Agent.Agent()
			agent.name = agentName
			agent.id = id
			agent.agentDesc = agentDesc
			self.addAgent( agentName, agent )
		return agent

		
	def load(self, progressRange):
		masProgress = int(0.1 * progressRange)
		cdlProgress = 0
		if len(self._cdlFiles):
			cdlProgress = int(int(0.1 * progressRange) / len(self._cdlFiles))
		callsheetProgress = int(0.1 * progressRange)
		simProgress = progressRange - masProgress - cdlProgress - callsheetProgress
		# If a MAS file was given parse it for the terrain file
		# and any additional CDL files. If no MAS file was given
		# the user has to specify the terrain file and CDL files
		# manually
		#
		if self._masFile:
			resolvedPath = self.resolvePath(self._masFile)
			
			Progress.setProgressStatus(os.path.basename(resolvedPath))
			Timer.push("Read MAS")
			
			fileHandle = open(resolvedPath, "r")
			try:
				mas = MasReader.read( fileHandle )
			finally:
				fileHandle.close()

			(mas.path, mas.masFile) = os.path.split(resolvedPath)
			self._terrainFile = mas.terrainFile
			self._cdlFiles = mas.cdlFiles
			
			Timer.pop()
			Progress.advanceProgress( masProgress )

			# store the user specified selections - they will be used
			# to filter any created agents
			for name in self._selectionNames:
				try:
					self._selectionGroup.addSelection( name, mas.selectionGroup.selection(name) )
				except:
					pass
		
		# Load the agent description of all specified CDL files
		#
		Timer.push("Read CDL")
		for cdlFile in self._cdlFiles:
			resolvedPath = self.resolvePath(cdlFile.file)
			Progress.setProgressStatus(os.path.basename(resolvedPath))
			# Loads the CDL file and stores the agent description in the
			# _agentDescriptions dict
			#
			self.agentDesc( resolvedPath, cdlFile.type )
			Progress.advanceProgress( cdlProgress )
		Timer.pop()
		
		# If a callsheet was given use it to fix the variable values
		# for all agent instances. Otherwise the variable values will be
		# random.
		#
		if self._callsheet:
			Timer.push("Read Callsheet")
			resolvedPath = self.resolvePath(self._callsheet)
			Progress.setProgressStatus( os.path.basename(resolvedPath) )
			
			CallsheetReader.read( resolvedPath, self )
			
			Progress.advanceProgress( callsheetProgress )
			Timer.pop()
		
		# Load the sim data if a sim dir was given.
		#
		simDir = self.simDir()
		if simDir:
			sim = Sim.Sim(self._selectionGroup)
			SimReader.read( simDir, self.simType, sim, simProgress )
			if (eAnimType.curves == self.animType):
				for agentSim in sim.agents():
					agent = self.agentByName( agentSim.name() )
					agent.setSim( agentSim )
			else:
				MsvSimLoader.sims[simDir] = sim
				for agentSim in sim.agents():
					agent = self.agentByName( agentSim.name() )
					# Record the start and end frames in case we're building
					# a geometry cache.
					#
					agent.sim().startFrame = agentSim.startFrame
					agent.sim().endFrame = agentSim.endFrame


				


		
