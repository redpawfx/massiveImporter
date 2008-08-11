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

import ns.bridge.io.AMCReader as AMCReader
import ns.bridge.io.WReader as WReader
import ns.bridge.data.AgentSpec as AgentSpec

def _resolvePath( rootPath, path ):
	resolved = path
	if resolved[0] == '+':
		resolved = resolved[1:]
	if rootPath and not os.path.isabs(resolved):
		resolved = "%s/%s" % (rootPath, resolved)
	return resolved

def _handleGeometry(fileHandle, tokens, agentSpec):
	'''Handle one piece of geometry'''
	
	geometry = AgentSpec.Geometry()
	if len(tokens) > 1:
		geometry.name = tokens[1]
	#file filename			The .obj file referenced by this geometry node.
	#flip_normals			Specifies whether normals should be flipped.
	#id n					Specifies the node's id number.
	#material n				The id of the material node assigned to this geometry node.
	#rotate x y z			Rotations applied to this geometry in Massive.
	#scale x y z			Scale transformations applied to this geometry in Massive.
	#translate x y z		Translation applied to this geometry in Massive.
	#translate x y			Specifies the location of the current node's icon in the icon work area.
	#weights_file filename	the .w file storing the skinning weights
	
	tokens = []
	for line in fileHandle:
		tokens = line.strip().split()
		if not line[0].isspace():
			break
		if tokens:
			if tokens[0] == "file":
				geometry.file = _resolvePath( agentSpec.rootPath(), tokens[1] )
			elif tokens[0] == "id":
				geometry.id = int(tokens[1])
			elif tokens[0] == "weights_file":
				geometry.weightsData = WReader.WReader()
				geometry.weightsData.read( _resolvePath( agentSpec.rootPath(), tokens[1] ) )
			elif tokens[0] == "material":
				geometry.material = int(tokens[1])
			elif tokens[0] == "attach":
				geometry.attach = tokens[1]
			else:
				geometry.leftovers += line
	
	agentSpec.geoDB.addGeometry(geometry)
	
	return line

def _handleCloth(fileHandle, tokens, agentSpec):
	'''Handle one piece of cloth. Since cloth isn't handled yet, treat it
	   as geometry.'''
	
	geometry = AgentSpec.Geometry()
	if len(tokens) > 1:
		geometry.name = tokens[1]
	#collide_ks value  		Specifies collision force.
	#collisions type 		Specifies type of collisions: terrain, skeleton, geometry. More than one may be specified.
	#drag value 			Specifies drag.
	#geo filename 			The .obj file referenced by this cloth node, if any.
	#grid x-res y-res x y	If cloth object is a grid, specifies x-resolution, y-resolution, x-size and y-size.
	#id n 					Specifies the node's id number.
	#kb value 				Specifies bend resistance.
	#ks value 				Specifies stretch resistance.
	#material n 			The id of the material node assigned to this cloth node.
	#rotate x y z 			Rotations applied to this cloth object.
	#scale x y z 			Scale transformations applied to this cloth object.
	#steps n 				Specifies number of steps for cloth dynamics.
	#thickness value 		Specifies cloth thickness.
	#translate x y z 		Translation applied to this cloth object.
	#translate x y 			Specifies the location of the current node's icon in the icon work area.		

	tokens = []
	for line in fileHandle:
		tokens = line.strip().split()
		if not line[0].isspace():
			break
		if tokens:
			if tokens[0] == "geo" and len(tokens) > 1:
				# The geo tag may be empty if this cloth node represents
				# an empty entry in an option node
				geometry.file = _resolvePath(agentSpec.rootPath(), tokens[1])
			elif tokens[0] == "id":
				geometry.id = int(tokens[1])
			elif tokens[0] == "material":
				geometry.material = int(tokens[1])
			else:
				geometry.leftovers = ""
	
	agentSpec.geoDB.addGeometry(geometry)
	
	return line

def _handleMaterial(fileHandle, tokens, agentSpec):
	'''Handle one material'''
	
	material = AgentSpec.Material()
	if len(tokens) > 1:
		material.name = tokens[1]
	#ambient value1 value2 value3 colourspace
	#	Specifies the OpenGL ambient value of the material. Example:
	#		ambient 0.5 0.5 0.7 hsv
	#colour_map filename type
	#	Specifies the OpenGL ambient value of the material. Example:
	#		colour_map /massive/agent1/maps/map1.tif rgb
	#diffuse value1 value2 value3 colourspace
	#	Specifies the OpenGL diffuse value of the material. Example:
	#		diffuse 0.5 0.5 0.7 hsv
	#id n	
	#	Specifies the node's id number.
	#rman_displacement shader name1 [value1] name2 [value2]...
	#	Specifies RenderMan displacement shader assigned to this material and
	#	its specified parameter values.
	#rman_surface shader name1 [value1] name2 [value2]...
	#	Specifies RenderMan surface shader assigned to this material and its
	#	specified parameter values.
	#specular value1 value2 value3 colourspace
	#	Specifies the OpenGL specular value of the material. Example:
	#		specular 0.5 0.5 0.7 hsv
	#translate x y
	#	Specifies the location of the current node's icon in the icon work
	#	area.
	
	tokens = []
	for line in fileHandle:
		tokens = line.strip().split()
		if not line[0].isspace():
			break
		if tokens:
			if tokens[0] == "colour_map":
				material.rawColorMap = _resolvePath( agentSpec.rootPath(), tokens[1] )
			elif tokens[0] == "id":
				material.id = int(tokens[1])
			elif tokens[0] == "ambient":
				for i in range(1,4):
					# color component is either a float value or a
					# variable/expression
					try:
						material.ambient[i-1] = float(tokens[i])
					except:
						material.ambientVar[i-1] = tokens[i]
				if len(tokens) > 4:
					material.ambientSpace = tokens[4]
			elif tokens[0] == "diffuse":
				for i in range(1,4):
					# color component is either a float value or a
					# variable/expression
					try:
						material.diffuse[i-1] = float(tokens[i])
					except:
						material.diffuseVar[i-1] = tokens[i]
				if len(tokens) > 4:
					material.diffuseSpace = tokens[4]
			elif tokens[0] == "specular":
				for i in range(1,4):
					# color component is either a float value or a
					# variable/expression
					try:
						material.specular[i-1] = float(tokens[i])
					except:
						material.specularVar[i-1] = tokens[i]
				if len(tokens) > 4:
					material.specularSpace = tokens[4]
			elif tokens[0] == "roughness":
					# roughness is either a float value or a
					# variable/expression
					try:
						material.roughness = float(tokens[1])
					except:
						material.roughnessVar = tokens[1]
			else:
				material.leftovers += line
		
	numMaterials = len(agentSpec.materialData)
	if material.id >= numMaterials:
		agentSpec.materialData.extend([ None ] * (material.id - numMaterials + 1))
	
	agentSpec.materialData[material.id] = material
	
	return line
	
def _handleOption(fileHandle, tokens, agentSpec):
	'''Handle one option node'''
	
	option = AgentSpec.Option()
	if len(tokens) > 1:
		option.name = "_".join(tokens[1:])
	# attach n1 n2 n3...
	#	Specifies id numbers of segment nodes this option node is bound to.
	# inputs n1 n2 n3...
	#	Specifies id numbers of geometry or cloth nodes attached to this
	#	option node.
	# translate x y
	#	Specifies the location of the current node's icon in the icon work
	#	area.
	# var name
	#	Specifies name of agent variable driving this option node.		
	tokens = []
	for line in fileHandle:
		tokens = line.strip().split()
		if not line[0].isspace():
			break
		if tokens:
			if tokens[0] == "translate":
				pass
			elif tokens[0] == "var":
				option.var = tokens[1]
			# TODO: I think inputs and geo are mutually exclusive.
			#		I should confirm and make sure that if both appear it
			#		is handled correctly.
			elif tokens[0] == "inputs":
				for input in tokens[1:]:
					option.inputs.append(agentSpec.geoDB.geometryByName(input))
			elif tokens[0] == "geo":
					for input in tokens[1:]:
						option.inputs.append(agentSpec.geoDB.geometryById(int(input)))
			else:
				option.leftovers += ""
		
	agentSpec.geoDB.addOption( option )
	
	return line
		
def _handleVariable(fileHandle, tokens, agentSpec):
	'''Handle a variable Spec'''
	
	# name default_value [min_value max_value] expression
	variable = AgentSpec.Variable()
	variable.name = tokens[1]
	variable.default = float(tokens[2])
	variable.min = float(tokens[3][1:])
	variable.max = float(tokens[4][:-1])	
	if len(tokens) >= 6:
		variable.expression = tokens[5]
	
	agentSpec.variables[variable.name] = variable
	return fileHandle.next()

def _handleSegment(fileHandle, tokens, agentSpec):
	'''Handle one segment'''
	
	joint = AgentSpec.Joint(agentSpec)
	if len(tokens) > 1:
		joint.name = tokens[1]
	
	#axis A 	 Specify the major axis for a tube primitive.
	axis = [ False, True, False ]
	#bone_rotate x y z 	Specify the tube primitive rotation with respect to segment space.
	bone_rotate = [ 0.0, 0.0, 0.0 ]
	#centre x y z 	Offset the primitive by x y z in segment space.
	centre = []
	#density value 	Density of the segment. (Mass is derived from this value.)
	#include filename 	Specifies the inclusion of the cdl file called filename.
	#length l 	Specifies the length of a tube or line primitive.
	length = 1.0
	#limits dof min max 	Sets the limits for the degree of freedom `dof'. One or more degrees of freedom may follow a single limits statment, one to a line.
	#order a b c d e f 	Specifies the order of transformations. a b c d e f can each be any of: tx ty tz rx ry rz.
	#rotateOrder = "xyz"
	#translateOrder = "xyz"
	#parent name 	Attaches the current segment to the named segment.
	#primitive type 	Specifies the type of segment: box, tube, sphere, line, billboard.
	primitive = ""
	#radius r 	Specifies the radius of a tube or sphere primitive.
	radius = 1.0
	#rotate x y z 	Specifies a rotation of segment rest space. Rotates x about the X axis, y about the Y axis and z about the Z axis. The units depend on the arguement given in the angles statement.
	rotate = []
	#scale x y z 	Specifies a scale of segment rest space.
	scale = [ 1.0, 1.0, 1.0 ]
	#segment name
	#size x y z 	Specifies the size of a box or billboard primitive.
	size = [ 1.0, 1.0, 1.0 ]
	#standin name 	Standins are like segments but can be rendered in place of an entire object. They are selected for rendering by comparing the distance from the camera with the threshold value.
	#
	#example :
	#
	#standin WHITE
	#  primitive billboard
	#  size 0.9000 1.7000 0.0000
	#  centre 0.0000 -0.3000 0.0000
	#  threshold 0.000
	#standin WHITE2
	#  parent WHITE
	#  primitive line
	#  length 1.7000
	#  axis Y
	#  centre 0.00000 -0.3000 0.0000
	#  threshold 10.0000
	#threshold d 	Specifies the threshold distance for a standin.
	#transform 	m00 m01 m02 m03
	#m10 m11 m12 m13
	#m20 m21 m22 m23
	#m30 m31 m32 m33
	#Loads the matrix m into the segment rest matrix. Ignores any previous transformations to the rest matrix.
	#translate x y z 	Specifies a translation of segment rest space.
	iconTranslate = [ 0, 0 ]
	# bind_pose x y z Offset to be applied when keying actions
	# dof rx ry rz tx ty tz Degrees of freedom limited to specified channels
	
	tokens = []
	for line in fileHandle:
		tokens = line.strip().split()
		if not line[0].isspace():
			break
		if tokens:
			if tokens[0] == "axis":
				axis = [ ("X" == tokens[1]), ("Y" == tokens[1]), ("Z" == tokens[1]) ]
			elif tokens[0] == "bone_rotate":
				bone_rotate = (float(tokens[1]), float(tokens[2]), float(tokens[3]))
			elif tokens[0] == "centre":
				centre = [ float(tokens[1]), float(tokens[2]), float(tokens[3]) ]
			elif tokens[0] == "length":
				length = tokens[1]
			elif tokens[0] == "order":
				# THEORY: maya and massive's rotation orders are reversed, if massive
				# says xyz, we have to use zyx in Maya
				translateOrder = []
				rotateOrder = []
				for i in range( 1, len(tokens) ):
					enum = AgentSpec.channel2Enum[tokens[i]]
					if AgentSpec.isRotateEnum( enum ):
						rotateOrder.append( enum )
					else:
						translateOrder.append( enum )
				joint.order = translateOrder
				joint.order.extend( rotateOrder )
			elif tokens[0] == "parent":
				joint.parent = tokens[1]
			elif tokens[0] == "primitive":
				primitive = tokens[1]
			elif tokens[0] == "radius":
				radius = tokens[1]
			elif tokens[0] == "rotate":
				rotate = [ float(tokens[1]), float(tokens[2]), float(tokens[3]) ]
			elif tokens[0] == "scale":
				scale = [ float(tokens[1]), float(tokens[2]), float(tokens[3]) ]
			elif tokens[0] == "size":
				size = [ float(tokens[1]), float(tokens[2]), float(tokens[3]) ]
			elif tokens[0] == "translate":
				if len(tokens) == 3:
					iconTranslate = [ float(tokens[1]), float(tokens[2]) ]
				else:
					joint.translate = (float(tokens[1]), float(tokens[2]), float(tokens[3]))
			elif tokens[0] == "transform":
				# Read the next 4 lines, tokenize them, cast them to 
				# float, and append them to the transform list
				#
				for i in range(4):
					joint.transform.extend([ float(tok) for tok in fileHandle.next().strip().split() ])
			elif tokens[0] == "dof":
				# Since dof was specified only the named channels are free
				#
				joint.dof = [ False ] * 6
				for channel in tokens[1:]:
					joint.dof[AgentSpec.channel2Enum[channel]] = True
			elif tokens[0] == "scale_var":
				joint.scaleVar = tokens[1]	
			elif tokens[0] == "bind_pose":
				# It seems like these values have to be subtracted from the
				# bind pose before the action is applied
				joint.actionOffset = [ -float(tokens[1]), -float(tokens[2]), -float(tokens[3]) ]
			else:
				joint.leftovers += line
			
	if "box" == primitive:
		joint.primitive = AgentSpec.Box(joint)
		joint.primitive.size = size
	elif "tube" == primitive:
		joint.primitive = AgentSpec.Tube(joint)
		joint.primitive.rotate = bone_rotate
		joint.primitive.radius = radius
		joint.primitive.length = length
	elif "sphere" == primitive:
		joint.primitive = AgentSpec.Sphere(joint)
		joint.primitive.radius = radius
	elif "disc" == primitive:
		joint.primitive = AgentSpec.Disc(joint)
		joint.primitive.radius = radius
		joint.primitive.length = length
				
	joint.primitive.axis = axis
	joint.primitive.centre = centre
	
	# Maps the Massive joint name to the joint object (for example
	# so that the AMCReader can get the degrees of freedom of a given
	# joint)
	#
	agentSpec.joints[joint.name] = joint
	# stores the order that the segments were encountered
	# we have to preserve this order when building the Maya
	# representation
	#
	agentSpec.jointData.append( joint )
	
	return line

def _handleCurve(fileHandle, tokens, action):
	'''Read one anim curve.'''
		
	tokens = fileHandle.next().strip().split()
	assert "channel" == tokens[0]
	channel = tokens[1]

	tokens = fileHandle.next().strip().split()
	assert "type" == tokens[0]
	type = tokens[1]

	tokens = fileHandle.next().strip().split()
	assert "points" == tokens[1]
	numPoints = int(tokens[0])
	
	curve = AgentSpec.Curve(channel, type, numPoints)
	
	for i in range(numPoints):
		tokens = fileHandle.next().strip().split()
		curve.points[i] = (float(tokens[0]), float(tokens[1]))
		
	action.addCurve( curve )

	
def _handleAction(fileHandle, tokens, agentSpec):
	'''Reads an embedded ASCII action.'''
	
	action = AgentSpec.Action()
	if len(tokens) > 1:
		action.name = tokens[1]
		
	for line in fileHandle:
		tokens = line.strip().split()
		if not line[0].isspace():
			break
		if tokens:
			if tokens[0] == "curve":
				_handleCurve(fileHandle, tokens, action)
			else:
				action.leftovers += line
	
	agentSpec.actions[action.name] = action
	
	return line

def _handleObject(fileHandle, tokens, agentSpec):
	''' Reads the object and id tags. The id tag must follow the object tag
		otherwise it won't be picked up - this is to avoid confusion with the
		id tags within blocks that we don't heanlde (e.g. fuzzy).'''
	
	agentSpec.agentType = tokens[1]
	line = fileHandle.next()
	tokens = line.strip().split()
	if (tokens[0] == "id"):
		agentSpec.id = int(tokens[1])
		line = fileHandle.next()
	
	return line

def _process(fileHandle, line, agentSpec):
	tokens = line.strip().split()
	while tokens:
		if tokens[0] == "variable":
			line = _handleVariable(fileHandle, tokens, agentSpec)
		elif tokens[0] == "scale_var":
			agentSpec.scaleVar = tokens[1]
			line = fileHandle.next()
		elif tokens[0] == "segment" :
			line = _handleSegment(fileHandle, tokens, agentSpec)
		elif tokens[0] == "material":
			line = _handleMaterial(fileHandle, tokens, agentSpec)
		elif tokens[0] == "cloth":
			line = _handleCloth(fileHandle, tokens, agentSpec)
		elif tokens[0] == "geometry":
			line = _handleGeometry(fileHandle, tokens, agentSpec)
		elif tokens[0] == "option":
			line = _handleOption(fileHandle, tokens, agentSpec)
		elif tokens[0] == "object":
			line = _handleObject(fileHandle, tokens, agentSpec)
		elif tokens[0] == "action":
			line = _handleAction(fileHandle, tokens, agentSpec)
		elif tokens[0] == "bind_pose":
			agentSpec.bindPoseFile = tokens[1]
			line = fileHandle.next()
		elif tokens[0] == "units":
			agentSpec.units = tokens[1]
			line = fileHandle.next()
		elif tokens[0] == "colour":
			agentSpec.color = float(tokens[1])
			line = fileHandle.next()
		elif tokens[0] == "angles":
			agentSpec.angles = tokens[1]
			line = fileHandle.next()
		else:
			if tokens[0] != "#":
				agentSpec.leftovers += line
			break
		
		tokens = line.strip().split()
	
	
def read(cdlFile):
	#
	
	agentSpec = AgentSpec.AgentSpec()
	rootPath = ""
	if isinstance(cdlFile, basestring):
		agentSpec.setCdlFile(cdlFile)
		fileHandle = open(cdlFile, "r")
	else:
		fileHandle = cdlFile
	
	try:
		try:
			for line in fileHandle:
				_process(fileHandle, line, agentSpec)
				
			if agentSpec.bindPoseFile:
				agentSpec.setBindPose(AMCReader.read(_resolvePath(agentSpec.rootPath(), agentSpec.bindPoseFile)))
				
		finally:
		 	if fileHandle != cdlFile:
		 		# I opened fileHandle so I have to close it
		 		fileHandle.close()	
	except:
		print >> sys.stderr, "Error reading CDL file."
		raise
	
	return agentSpec


