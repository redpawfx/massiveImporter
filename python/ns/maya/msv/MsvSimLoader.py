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

import maya
from maya.OpenMaya import *
from maya.OpenMayaMPx import *

import ns.py as npy
import ns.py.Errors

import ns.bridge.data.SimData as SimData
import ns.bridge.io.SimReader as SimReader
import ns.bridge.data.Selection as Selection
import ns.bridge.data.AgentSpec as AgentSpec
import ns.bridge.data.Agent as Agent

kName = "msvSimLoader"

kId = MTypeId(0x00037047)

# Node definition
class MsvSimLoader(MPxNode):
	# class variables
	aTime = MObject()
	aSimDir = MObject()
	aAgentType = MObject()
	aInstance = MObject()
	aSimType = MObject()
	aJoints = MObject()
	aOffsets = MObject()
	aTranslateOffset = MObject()
	aRotateOffset = MObject()
	
	aOutput = MObject()
	aTranslate = MObject()
	aRotate = MObject()
	
	sims = {}
	
	def __init__(self):
		MPxNode.__init__(self)
		
	def postConstructor(self):
		self.setExistWithoutInConnections(True)
		self.setExistWithoutOutConnections(False)
		
	def compute(self, plug, dataBlock):
		'''Calculate the output translate and rotate values. If any value is
		   queried, all of them are updated and cleaned.'''
		try:
			if ( plug == MsvSimLoader.aOutput or
				 plug == MsvSimLoader.aTranslate or
				 plug == MsvSimLoader.aRotate ):
				
				#==============================================================
				# Query Input Attributes
				#==============================================================
				simDir = self._asString( dataBlock.inputValue( MsvSimLoader.aSimDir ) )
				if not simDir or not os.path.isdir(simDir):
					raise npy.Errors.BadArgumentError("Please set the simDir attribute to a valid directory path.")
				
				agentType = self._asString( dataBlock.inputValue( MsvSimLoader.aAgentType ) )
				if not agentType:
					raise npy.Errors.BadArgumentError("Please set the agentType attribute.")

				instance = dataBlock.inputValue( MsvSimLoader.aInstance ).asInt()
	
				frame = int(dataBlock.inputValue( MsvSimLoader.aTime ).asTime().value())

				simType = self._asString( dataBlock.inputValue( MsvSimLoader.aSimType ) )
				simType = ".%s" % simType

				#==============================================================
				# Query the cached sim data, or read it from disk if no cache
				# exists
				#==============================================================				
				try:
					sim = MsvSimLoader.sims[simDir]
				except:
					sim = SimData.SimData()
					SimReader.read( simDir, simType, sim )
					MsvSimLoader.sims[simDir] = sim
				
				#==============================================================
				# Get the sim data for the target agent
				#==============================================================
				agentName = Agent.formatAgentName( agentType, instance )
				agentSim = sim.agent(agentName)
				if agentSim: 
					#==========================================================
					# Iterate over the input joints and query their translate
					# and rotate values from the sim data. Add the
					# corresponding offset and stuff the result in 'output'.
					#==========================================================
					haJoints = dataBlock.inputArrayValue( MsvSimLoader.aJoints )
					haOffsets = dataBlock.inputArrayValue( MsvSimLoader.aOffsets )
					haOutput = dataBlock.outputArrayValue( MsvSimLoader.aOutput )
					for i in range(haJoints.elementCount()):
						# Assume that both the 'joints' and 'output' multis
						# have the same number of elements and are not sparse
						haJoints.jumpToArrayElement(i)
						jointName = self._asString( haJoints.inputValue() )
						jointSim = agentSim.joint(jointName)

						# 'output' is a multi-compound with one entry for every
						# entry in the 'joints' input multi. The compound
						# children are also multis, with one element for every
						# channel in the corresponding joint's sim data. By
						# iterating over the elements in the 'translate' and
						# 'rotate' compound children we know how many samples
						# to query from the joint sim.
						#
						# 'offsets' is structured the same as 'output' and
						# stores the translate and rotate offsets for a given
						# channel.
						sampleIndex = 0
						haOffsets.jumpToArrayElement(i)
						haOutput.jumpToArrayElement(i)
						# The joint sim stores sample data as an array and
						# without distinguishing between translate and rotate
						# samples. 'sampleIndex' will keep track of where we
						# are in that array.
						haTranslateOffset = MArrayDataHandle( haOffsets.inputValue().child( MsvSimLoader.aTranslateOffset ) )
						haTranslate = MArrayDataHandle( haOutput.outputValue().child( MsvSimLoader.aTranslate ) )
						for j in range(haTranslate.elementCount()):
							# Get the sample data
							sample = jointSim.sampleByIndex( sampleIndex, frame )
							# Add the offset
							haTranslateOffset.jumpToArrayElement(j)
							sample += haTranslateOffset.inputValue().asDistance().value()
							# Stuff it in the output
							distance = MDistance( sample )
							haTranslate.jumpToArrayElement(j)
							haTranslate.outputValue().setMDistance( distance )
							# Increment sampleIndex so we know what sample to
							# query from the jointSim
							sampleIndex += 1
						haTranslate.setAllClean()
						
						haRotateOffset = MArrayDataHandle( haOffsets.inputValue().child( MsvSimLoader.aRotateOffset ) )
						haRotate = MArrayDataHandle( haOutput.outputValue().child( MsvSimLoader.aRotate ) )
						for j in range(haRotate.elementCount()):
							# Get the sample data
							sample = jointSim.sampleByIndex( sampleIndex, frame )
							# Add the offset
							haRotateOffset.jumpToArrayElement(j)
							sample += haRotateOffset.inputValue().asAngle().value()
							# Stuff it in the output
							angle = MAngle( sample, MAngle.kDegrees )
							haRotate.jumpToArrayElement(j)
							haRotate.outputValue().setMAngle( angle )
							# Increment sampleIndex so we know what sample to
							# query from the jointSim
							sampleIndex += 1
						haRotate.setAllClean()
					haOutput.setAllClean()
				return MStatus.kSuccess
		except ns.py.Errors.Error, e:
			MGlobal.displayError("Error: %s" % e)
			return MStatus.kFailure
		
		return MStatus.kUnknownParameter
	
	def _asString(self, dataHandle):
		'''Workaround for API limitation: MDataHandle::asString() returns
		   MString instead of python string.'''
		try:
			return MFnStringData( dataHandle.data() ).string()
		except:
			# MFnStringData throws an exception if the the dataHandle has not
			# been set.
			return ""
	
# creator
def nodeCreator():
	return asMPxPtr( MsvSimLoader() )

# initializer
def nodeInitializer():
	'''Create the msvSimLoader attributes'''
	# time
	fAttr = MFnUnitAttribute()
	MsvSimLoader.aTime = fAttr.create( "time", "tim", MFnUnitAttribute.kTime )
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
		
	# simDir
	fAttr = MFnTypedAttribute()
	MsvSimLoader.aSimDir = fAttr.create( "simDir", "sd", MFnData.kString )
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# agentType
	fAttr = MFnTypedAttribute()
	MsvSimLoader.aAgentType = fAttr.create( "agentType", "at", MFnData.kString )
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# instance
	fAttr = MFnNumericAttribute()
	MsvSimLoader.aInstance = fAttr.create( "instance", "i", MFnNumericData.kInt,1 )
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# simType
	fString = MFnStringData()
	fAttr = MFnTypedAttribute()
	MsvSimLoader.aSimType = fAttr.create( "simType", "st", MFnData.kString, fString.create("apf") )
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# joints
	fAttr = MFnTypedAttribute()
	MsvSimLoader.aJoints = fAttr.create( "joints", "j", MFnData.kString )
	fAttr.setArray(True)
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# offsets.translateOffset
	fAttr = MFnUnitAttribute()
	MsvSimLoader.aTranslateOffset = fAttr.create( "translateOffset", "to", MFnUnitAttribute.kDistance )
	fAttr.setArray(True)
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# offsets.rotateOffset
	fAttr = MFnUnitAttribute()
	MsvSimLoader.aRotateOffset = fAttr.create( "rotateOffset", "ro", MFnUnitAttribute.kAngle )
	fAttr.setArray(True)
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# offsets
	fAttr = MFnCompoundAttribute()
	MsvSimLoader.aOffsets = fAttr.create( "offsets", "off" )
	fAttr.addChild( MsvSimLoader.aTranslateOffset )
	fAttr.addChild( MsvSimLoader.aRotateOffset )
	fAttr.setArray(True)
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	
	# output.translate
	fAttr = MFnUnitAttribute()
	MsvSimLoader.aTranslate = fAttr.create( "translate", "t", MFnUnitAttribute.kDistance )
	fAttr.setArray(True)
	fAttr.setKeyable(False)
	fAttr.setWritable(False)
	fAttr.setReadable(True)
	fAttr.setStorable(False)
	
	# output.rotate
	fAttr = MFnUnitAttribute()
	MsvSimLoader.aRotate = fAttr.create( "rotate", "r", MFnUnitAttribute.kAngle )
	fAttr.setArray(True)
	fAttr.setKeyable(False)
	fAttr.setWritable(False)
	fAttr.setReadable(True)
	fAttr.setStorable(False)
	
	# output
	fAttr = MFnCompoundAttribute()
	MsvSimLoader.aOutput = fAttr.create( "output", "o" )
	fAttr.addChild( MsvSimLoader.aTranslate )
	fAttr.addChild( MsvSimLoader.aRotate )
	fAttr.setArray(True)
	fAttr.setKeyable(False)
	fAttr.setWritable(False)
	fAttr.setReadable(True)
	fAttr.setStorable(False)
		
	# add attributes
	MsvSimLoader.addAttribute( MsvSimLoader.aTime )
	MsvSimLoader.addAttribute( MsvSimLoader.aSimDir )
	MsvSimLoader.addAttribute( MsvSimLoader.aAgentType )
	MsvSimLoader.addAttribute( MsvSimLoader.aInstance )
	MsvSimLoader.addAttribute( MsvSimLoader.aSimType )
	MsvSimLoader.addAttribute( MsvSimLoader.aJoints )
	MsvSimLoader.addAttribute( MsvSimLoader.aOffsets )
	MsvSimLoader.addAttribute( MsvSimLoader.aOutput )

	MsvSimLoader.attributeAffects( MsvSimLoader.aTime, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimDir, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aAgentType, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aInstance, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimType, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aJoints, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aOffsets, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aTranslateOffset, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aRotateOffset, MsvSimLoader.aOutput )

	MsvSimLoader.attributeAffects( MsvSimLoader.aTime, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimDir, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aAgentType, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aInstance, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimType, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aJoints, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aOffsets, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aTranslateOffset, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aRotateOffset, MsvSimLoader.aTranslate )

	MsvSimLoader.attributeAffects( MsvSimLoader.aTime, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimDir, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aAgentType, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aInstance, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimType, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aJoints, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aOffsets, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aTranslateOffset, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aRotateOffset, MsvSimLoader.aRotate )
	