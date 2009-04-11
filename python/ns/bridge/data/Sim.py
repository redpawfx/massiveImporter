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

import ns.bridge.io.CallsheetReader as CallsheetReader
import ns.bridge.data.Selection as Selection
import ns.bridge.data.Agent as Agent
import ns.bridge.data.SimData as SimData
import ns.bridge.io.SimReader as SimReader
import ns.py as npy
import ns.py.Errors

class Sim:
	'''Load files and collect data related to a Massive simulation.
	   This includes callsheets and simmed .apf or .amc files.'''
	def __init__(self, scene, simDir, simType, callsheet=None,
				 selectionNames=[], range=""):
		self.scene = scene
		self.simDir = simDir
		self.simType = simType
		self.callsheet = callsheet
		self.range = range
		self._selectionGroup = self._initSelection(selectionNames, range)
		self._agents = {}
		self._load()

	def agents( self ):
		return self._agents.values()

	def agent(self, agentName, id, agentSpec):
		'''If the given agent already exists, return it. Otherwise guess
		   its agent type and id based on its name, and build a new agent
		   with the appropriate AgentSpec. If no AgentSpec exists for that
		   type, raise an error. This method also handles filtering out
		   agents that do not exist in the user specified "selections"'''
			
		if not self._selectionGroup.contains( id ):
			# Filter out non-selected agents
			#
			return None
		
		try:
			agent = self._agents[agentName]
		except:
			# agentName does not already exist (probably no callsheet was
			# provided) - build one *if* the agentType is defined. The
			# agentType should have already been defined if a CDL file
			# was specified in the MAS file for the agentType.
			#
			if not agentSpec:
				agentSpec = self.scene.agentSpec(self._agentType(agentName))
			
			agent = Agent.Agent()
			agent.name = agentName
			agent.id = id
			agent.agentSpec = agentSpec
			self._agents[agentName] = agent
		return agent
	
	def _agentType(self, agentName):
		'''If this agent exists, query its agentType, otherwise try to 
		   guess its agentType by parsing its name. Massive agents are usually
		   named like: agentType_id'''
		agentType = ""
		try:
			agentType = self._agents[agentName].agentType
		except:
			agentType = agentName.split("_")[0]
		return agentType
	
	def _initSelection(self, selectionNames, range):
		'''Only agents in the _selectionGroup will be created and simmed. The
		   user can set the _selectionGroup by manually listing the selections
		   that should be loaded AND by specifying ranges of agent ids.'''
		selectionGroup = Selection.SelectionGroup()
		
		# store the user specified selections - they will be used
		# to filter any created agents
		for name in selectionNames:
			try:
				selectionGroup.addSelection( name, self.scene.mas().selectionGroup.selection(name) )
			except:
				print >> sys.stderr, "Warning: %s is not a valid selection." % name
				pass
		
		if range:
			tokens = range.split()
			sel = Selection.Selection()
			sel.addRanges(tokens)
			selectionGroup.addSelection( "NimbleMsv", sel )
		
		return selectionGroup
		
	def _load(self):
		'''Build agents and load their sim data. If a callsheet was given it
		   will fix the variable values for all agent instances. Otherwise the
		   variable values will be random.'''
		
		if self.callsheet:
			# The CallsheetReader will create agent instances for any agents
			# specified.
			CallsheetReader.read(self.callsheet, self)
			
		if self.simDir:
			self._simData = SimData.SimData(self._selectionGroup)
			SimReader.read(self.simDir, self.simType, self._simData)
			for agentSim in self._simData.agents():
				try:
					agent = self._agents[agentSim.name()]
				except KeyError:
					raise npy.Errors.UnitializedError("Agent %s does not exist. Perhaps the callsheet does not match the sim directory?" % agentSim.name())
				agent.setSimData(agentSim)

		