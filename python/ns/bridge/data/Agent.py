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
import random
import re
import os.path

import ns.bridge.data.SimData as SimData

def formatAgentName(name, id=""):
	'''Convenience function to make sure all of the agent
	   names are consistent. Sometimes they are read in
	   two parts, and sometimes that use a '.' as a delimeter,
	   etc...'''
	agentName = name
	if id:
		agentName = "%s_%s" % (name, id)
	agentName = re.sub('\.', '_', agentName)
	return agentName

class Agent:
	def __init__(self, instanced=True):
		self._instanced = instanced
		self.reset()
	
	def reset(self):
		self.name = ""
		self.id = -1
		self.agentSpec = None
		self.variableValues = {}
 		self.placement = [ 1.0, 0.0, 0.0, 0.0,
						   0.0, 1.0, 0.0, 0.0,
						   0.0, 0.0, 1.0, 0.0,
						   0.0, 0.0, 0.0, 1.0 ]
 		self._simData = SimData.Agent("")

	def joint(self, jointName):
		return self.agentSpec.joints[jointName]

	def simData(self):
		return self._simData
	
	def setSimData(self, simData):
		self._simData = simData
		self._simData.prune( self.agentSpec.joints.keys() )
		for jointSim in self._simData.joints():
			joint = self.joint( jointSim.name() )
			jointSim.setOrderDOF( joint.order, joint.dof )


	def replaceEmbeddedVariables( self, s ):
		'''Replaces variables that have been embedded in a string with their
		   current value.
		   Embedded variables are always delimited by single-quotes.'''
		replaced = s
		matches = re.search("'(\w*)'", s)
		if matches:
			value = self.variableValue( matches.group(1), asInt=True )
			replaced = re.sub("'\w*'", `value`, s)
		return replaced
		
	def evalExpression( self, rawExpression ):
		'''Evaluates a variable's expression.
		   This is different from replacing embedded variables like
		   those found in texture paths. Expressions don't delimit
		   variable names with quotes so we have to search the expression
		   for every possible variable'''
		expr = rawExpression
		for var in self.agentSpec.variables.keys():
			matches = re.search( var, expr )
			if matches:
				value = self.variableValue(matches.group(0))
				expr = re.sub(var, `value`, expr)
		return float(eval(expr))
				
	
	def variableValue( self, variableName, asInt=False, forceDefault=False ):
		'''Return the current value of the variable.
		   If the variable's value has been fixed via a sim, use the fixed
		   value. If no fixed value exists, either evaluate the variable's
		   expression or return a random number within its range. Finally
		   if variation has been disabled for this variable, return its
		   default value.'''
		   
		try:
			# Variable has been fixed by a sim or computed earlier
			#
			value = self.variableValues[variableName]
		except:
			# In calculating the value we have a few options:
			# 1. This variable doesn't actually exist, assign 0
			# 2. 'forceDefault' is true, assign the variable's default
			# 3. Variable has an expression and 'forceDefault' is false, evaluate it
			# 3. No expression and 'forceDefault' is false
			#	 a. agent is instanced, assign a random value
			#		Note: this shouldn't happen if a callsheet was provided
			#	 b. agent is not-instanced, assign the variable's default
			variable = None
			try:
				variable = self.agentSpec.variables[variableName]
				useDefault = False
				if forceDefault:
					useDefault = True
				elif variable.expression:
					value = self.evalExpression( variable.expression )
				elif self._instanced:
					value = random.uniform( variable.min, variable.max )
				else:
					useDefault = True
			except:
				# Probably couldn't find a variable. In any case,
				# use the default value.
				useDefault = True
				
			if useDefault:
				if variable:
					# Default value will be used if we're not instanced
					value = variable.default
				else:
					value = 0.0
					
			# Store the computed variable value so that repeated
			# queries of the same variable will return the same
			# value
			#
			self.variableValues[variableName] = value
			
		# Round to an integer if needed
		#
		if asInt:
			value = int(round(value))			
			
		return value
