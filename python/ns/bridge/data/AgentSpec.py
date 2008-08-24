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
import re
import os.path

import ns.bridge.io.WReader as WReader
import ns.bridge.data.Brain as Brain

kTX, kTY, kTZ, kRX, kRY, kRZ = range(6)
channel2Enum = dict([["tx", kTX], ["ty", kTY], ["tz", kTZ], ["rx", kRX], ["ry", kRY], ["rz", kRZ]])
enum2Channel = ["tx", "ty", "tz", "rx", "ry", "rz"]
def isRotateEnum( channelEnum ):
	return channelEnum >= kRX

def isTranslateEnum( channelEnum ):
	return channelEnum < kRX

class Material:
	'''Imported'''
	def __init__(self):
		self.name = ""
		self.id = 0
		self.rawColorMap = ""
		self.specular = [ 0.0, 0.0, 0.0 ]
		self.specularVar = [ "", "", "" ]
		self.specularSpace = "hsv"
		self.ambient = [ 0.0, 0.0, 0.0 ]
		self.ambientVar = [ "", "", "" ]
		self.ambientSpace = "hsv"
		self.diffuse = [ 0.0, 0.0, 0.0 ]
		self.diffuseVar = [ "", "", "" ]
		self.diffuseSpace = "hsv"
		self.roughness = 0.02
		self.roughnessVar = ""
		self.leftovers = ""

class Geometry:
	'''Imported'''
	def __init__(self):
		self.name = ""
		self.file = ""
		self.id = 0
		self.material = 1
		self.weightsData = None
		self.attach = ""
		self.leftovers = ""
	
	def deformers( self ):
		if self.weightsData:
			return self.weightsData.deformers
		else:
			return []
	
	def weights( self ):
		if self.weightsData:
			return self.weightsData.weights
		else:
			return[]

class Option:
	def __init__(self):
		self.name = ""
		self.var = ""
		self.inputs = []
		self.leftovers = ""

class GeoDB:
	def __init__(self):
		self._byId = []
		self._byName = {}
		self._optioned = {}
	
	def geometryByName( self, name ):
		return self._byName[name]
	
	def geometryById( self, id ):
		return self._byId[id]
	
	def addGeometry(self, geometry):
 		numGeo = len(self._byId)
 		if geometry.id >= numGeo:
 			self._byId.extend([ None ] * (geometry.id - numGeo + 1))
 			
 		self._byId[geometry.id] = geometry
 		self._byName[geometry.name] = geometry
 		self._optioned[geometry.name] = geometry
 
	def addOption(self, option):
		for input in option.inputs:
			try:
				if not isinstance( self._optioned[input.name], Geometry ):
					continue
				self._optioned.pop(input.name)
			except:
				pass
			
		self._optioned[option.name] = option	


class GeoIter:
	def __init__(self, db, agent):
		self._db = db
		self._agent = agent
		self._list = db._optioned.values()
		self._last = len(self._list) - 1
		self._index = -1
		
	def __iter__(self):
		return self
	
	def next(self):
		if self._index >= self._last:
			raise StopIteration
		self._index += 1
		item = self._list[self._index]
		if isinstance( item, Option ):
			# item is an Option instance. Check the variable value and convert
			# it to the appropriate Geometry instance.
			# Some option nodes may use variables that can take more values
			# than there are options - make sure we don't get an index out
			# of bounds.
			#
			value = min(self._agent.variableValue(item.var, asInt=True), len(item.inputs) - 1)
			item = item.inputs[value]
		
		assert isinstance(item, Geometry)
		return item
		

class Curve:
	def __init__(self, channel, type, numPoints):
		self.channel = channel
		self.type = type
		self.points = [()] * numPoints
	
	def __str__(self):
		'''channel (type): point point point ...'''
		str = "%s (%s):" % (self.channel, self.type)
		for point in self.points:
			if point:
				str += " (%s, %s)" % point
		return str

class Action:
	def __init__(self):
		self.name = ""
		self.curves = {}
		self.maxPoints = 0
		self.leftovers = ""
	
	def addCurve( self, curve ):
		if curve.type == "linear":
 		 	tokens = curve.channel.split(":")
 		 	if len(tokens) == 1:
 		 		object = ""
 		 		attr = tokens[0]
  		 	else:
 		 		object = tokens[0]
 		 		attr = tokens[1]
  		 		
 		 	if len(curve.points) > self.maxPoints:
 		 		self.maxPoints = len(curve.points)
 		 	 
  		 	self.curves[ "%s %s" % (object, attr) ] = curve
  		 	
  	def __str__(self):
  		'''name
  		   		curve
  		   		curve
  		   		...
  		'''
  		str = self.name
  		for curve in self.curves.values():
  			str += "\n\t%s" % curve
  		return str

class Primitive:
	'''Imported'''
	def __init__(self, joint):
		self.joint = joint
		self.rotate = [ 0.0, 0.0, 0.0 ]
		self.axis = [ False, True, False ]
		self.centre = [ 0.0, 0.0, 0.0 ]
					
class Tube(Primitive):
	'''Imported'''
	def __init__(self, joint):
		Primitive.__init__(self, joint)
		self.radius = 1.0
		self.length = 1.0		

class Sphere(Primitive):
	'''Imported'''
	def __init__(self, joint):
		Primitive.__init__(self, joint)
		self.radius = 1.0

class Box(Primitive):
	'''Imported'''
	def __init__(self, joint):
		Primitive.__init__(self, joint)
		self.size = [ 1.0, 1.0, 1.0 ]
	
class Disc(Primitive):
	'''Imported'''
	def __init__(self, joint):
		Primitive.__init__(self, joint)
		self.radius = 1.0
		self.length = 1.0

class Joint:
	'''Imported'''
 	def __init__(self, agentSpec):
 		self.name = ""
 		self.parent = ""
 		self.dof = [ True ] * 6
 		self.primitive = None
 		self.order = [ kTX, kTY, kTZ, kRX, kRY, kRZ ]
 		self.actionOffset = [ 0, 0, 0 ]
 		self.translate = []
 		self.transform = []
		self.scaleVar = ""
 		self.agentSpec = agentSpec
 		self.leftovers = ""

class Variable:
	def __init__(self):
		self.name = ""
		self.min = 0.0
		self.max = 0.0
		self.default = 0.0
		self.expression = ""

# Node definition
class AgentSpec:
	def __init__(self):
		self.reset()
	
	def reset(self):
		# public
		self.cdlFile = ""
		self.agentType = ""
		self.bindPoseFile = ""
		self.scaleVar = ""
		# represented as SimData.Joint - but there will only be one frame of data
		self.bindPoseData = None
		self.jointData = []
		self.geoDB = GeoDB()
		self.materialData = []
		self.actions = {}
		self.variables = {}
		self.brain = Brain.Brain()
		# map Massive joint name to the joint object
		self.joints = {}
		self.leftovers = {}
		self.cdlStructure = []
		
		# private
		self._rootPath = ""
	
	def setCdlFile(self, cdlFile):
		self.cdlFile = cdlFile
		self._rootPath = os.path.dirname(cdlFile)
		
	def setBindPose(self, agentSim):
		self.bindPoseData = agentSim
		self.bindPoseData.prune( self.joints.keys() )
		for jointSim in self.bindPoseData.joints():
			joint = self.joints[ jointSim.name() ]
			jointSim.setOrderDOF( joint.order, joint.dof )
			
	def rootPath(self):
		return self._rootPath
   
