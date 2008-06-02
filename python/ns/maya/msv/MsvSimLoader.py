import sys
import os
import os.path

import maya
from maya.OpenMaya import *
from maya.OpenMayaMPx import *

import ns.py as npy
import ns.py.Errors

import ns.maya.msv.Sim as Sim
import ns.maya.msv.APFReader as APFReader
import ns.maya.msv.AMCReader as AMCReader
import ns.maya.msv.Selection as Selection
import ns.maya.msv.AgentDescription as AgentDescription

kName = "msvSimLoader"

kId = MTypeId(0x87001)

# Node definition
class MsvSimLoader(MPxNode):
	# class variables
	aTime = MObject()
	aSimDir = MObject()
	aAgentType = MObject()
	aInstance = MObject()
	aFileType = MObject()
	aJoints = MObject()
	
	aOutput = MObject()
	aTranslate = MObject()
	aRotate = MObject()
	
	def __init__(self):
		MPxNode.__init__(self)
		
	def postConstructor(self):
		self.setExistWithoutInConnections(True)
		self.setExistWithoutOutConnections(False)
		
	def compute(self, plug, dataBlock):
		try:
			if ( plug == MsvSimLoader.aOutput or
				 plug == MsvSimLoader.aTranslate or
				 plug == MsvSimLoader.aRotate ):
				
				simDir = self._asString( dataBlock.inputValue( MsvSimLoader.aSimDir ) )
				if not simDir or not os.path.isdir(simDir):
					raise npy.Errors.BadArgumentError("Please set the simDir attribute to a valid directory path.")
				
				agentType = self._asString( dataBlock.inputValue( MsvSimLoader.aAgentType ) )
				if not agentType:
					raise npy.Errors.BadArgumentError("Please set the agentType attribute.")

				instance = dataBlock.inputValue( MsvSimLoader.aInstance ).asInt()
	
				frame = int(dataBlock.inputValue( MsvSimLoader.aTime ).asTime().value())

				fileType = self._asString( dataBlock.inputValue( MsvSimLoader.aFileType ) )
				
				fileName = ""
				sel = Selection.SelectionGroup()
				sel.addAnonymousSelection( [ instance ] )
				sim = Sim.Sim(sel)
				simFile = None
				if "apf" == fileType:
					fileName = "%s/frame.%d.apf" % (simDir, frame)
					simFile = APFReader.APFReader(fileName)
				elif "amc" == fileType:
					fileName = "%s/%s.%d.amc" % (simDir, agentType, instance)
					simFile = AMCReader.AMCReader(fileName)
				else:
					raise npy.Errors.BadArgumentError("%s is an unsupported sim filetype." % fileType)
			
				simFile.read(sim)
				
				agentName = AgentDescription.formatAgentName( agentType, instance )
				agentSim = sim.agent(agentName)
				if agentSim: 
					haJoints = dataBlock.inputArrayValue( MsvSimLoader.aJoints )
					haOutput = dataBlock.outputArrayValue( MsvSimLoader.aOutput )
					for i in range(haJoints.elementCount()):
						haJoints.jumpToArrayElement(i)
						haOutput.jumpToArrayElement(i)
						jointName = self._asString( haJoints.inputValue() )
						jointSim = agentSim.joint(jointName)
						sampleIndex = 0
						haTranslate = MArrayDataHandle( haOutput.outputValue().child( MsvSimLoader.aTranslate ) )
						for j in range(haTranslate.elementCount()):
							haTranslate.jumpToArrayElement(j)
							sample = jointSim.sampleByIndex( sampleIndex, frame )
							distance = MDistance( sample )
							haTranslate.outputValue().setMDistance( distance )
							sampleIndex += 1
						haTranslate.setAllClean()
						haRotate = MArrayDataHandle( haOutput.outputValue().child( MsvSimLoader.aRotate ) )
						for j in range(haRotate.elementCount()):
							haRotate.jumpToArrayElement(j)
							sample = jointSim.sampleByIndex( sampleIndex, frame )
							angle = MAngle( sample, MAngle.kDegrees )
							haRotate.outputValue().setMAngle( angle )
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
	
	# fileType
	fString = MFnStringData()
	fAttr = MFnTypedAttribute()
	MsvSimLoader.aFileType = fAttr.create( "fileType", "ft", MFnData.kString, fString.create("apf") )
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
	MsvSimLoader.addAttribute( MsvSimLoader.aFileType )
	MsvSimLoader.addAttribute( MsvSimLoader.aJoints )
	MsvSimLoader.addAttribute( MsvSimLoader.aOutput )

	MsvSimLoader.attributeAffects( MsvSimLoader.aTime, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimDir, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aAgentType, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aInstance, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aFileType, MsvSimLoader.aOutput )
	MsvSimLoader.attributeAffects( MsvSimLoader.aJoints, MsvSimLoader.aOutput )

	MsvSimLoader.attributeAffects( MsvSimLoader.aTime, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimDir, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aAgentType, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aInstance, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aFileType, MsvSimLoader.aTranslate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aJoints, MsvSimLoader.aTranslate )

	MsvSimLoader.attributeAffects( MsvSimLoader.aTime, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aSimDir, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aAgentType, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aInstance, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aFileType, MsvSimLoader.aRotate )
	MsvSimLoader.attributeAffects( MsvSimLoader.aJoints, MsvSimLoader.aRotate )
	