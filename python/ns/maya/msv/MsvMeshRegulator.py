import maya
from maya.OpenMaya import *
from maya.OpenMayaMPx import *

kName = "msvMeshRegulator"

kId = MTypeId(0x87000)

# Node definition
class MsvMeshRegulator(MPxNode):
	# class variables
	aInMesh = MObject()
	aNullMesh = MObject()
	aPassThrough = MObject()
	aOutMeshes = MObject()
	
	def __init__(self):
		MPxNode.__init__(self)
		
	def postConstructor(self):
		self.setExistWithoutInConnections(True)
		
	def compute(self, plug, dataBlock):
		if ( plug == MsvMeshRegulator.aOutMeshes ):
			ahPassThrough = dataBlock.inputArrayValue( MsvMeshRegulator.aPassThrough )
			ahOutMeshes = dataBlock.outputArrayValue( MsvMeshRegulator.aOutMeshes )
			
			if ( ahPassThrough.elementCount() != ahOutMeshes.elementCount() ):
				MGlobal.displayError("passThrough and outMeshes attributes do not have the same number of elements.")
				return MStatus.kFailure
			
			for i in range(ahOutMeshes.elementCount()):
				ahPassThrough.jumpToArrayElement(i)
				passThrough = ahPassThrough.inputValue().asInt()
				ahOutMeshes.jumpToArrayElement(i)
				if passThrough:
					ahOutMeshes.outputValue().copy( dataBlock.inputValue( MsvMeshRegulator.aInMesh ) )
				else:
					ahOutMeshes.outputValue().copy( dataBlock.inputValue( MsvMeshRegulator.aNullMesh ) )
			
			dataBlock.setClean( plug )
			return MStatus.kSuccess

		return MStatus.kUnknownParameter
	
# creator
def nodeCreator():
	return asMPxPtr( MsvMeshRegulator() )

# initializer
def nodeInitializer():
	# inMesh
	fAttr = MFnTypedAttribute()
	MsvMeshRegulator.aInMesh = fAttr.create( "inMesh", "in", MFnData.kMesh )
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	fAttr.setCached(True)
	# nullMesh
	fAttr = MFnTypedAttribute()
	MsvMeshRegulator.aNullMesh = fAttr.create( "nullMesh", "nul", MFnData.kMesh )
	fAttr.setKeyable(False)
	fAttr.setWritable(False)
	fAttr.setReadable(False)
	fAttr.setStorable(False)
	fAttr.setCached(True)
	
	fNullMeshData = MFnMeshData()
	oNullMesh = fNullMeshData.create()
	fNullMesh = MFnMesh()
	fNullMesh.create( 0, 0,
					  MFloatPointArray(), MIntArray(), MIntArray(),
					  oNullMesh )
	fAttr.setDefault( oNullMesh )
	# outMeshes
	fAttr = MFnTypedAttribute()
	MsvMeshRegulator.aOutMeshes = fAttr.create( "outMeshes", "out", MFnData.kMesh )
	fAttr.setArray(True)
	fAttr.setKeyable(False)
	fAttr.setWritable(False)
	fAttr.setReadable(True)
	fAttr.setStorable(False)
	fAttr.setCached(False)
	# passThrough
	fAttr = MFnNumericAttribute()
	MsvMeshRegulator.aPassThrough = fAttr.create( "passThrough", "pt", MFnNumericData.kInt, 0 )
	fAttr.setArray(True)
	fAttr.setKeyable(True)
	fAttr.setWritable(True)
	fAttr.setReadable(True)
	fAttr.setStorable(True)
	# add attributes
	MsvMeshRegulator.addAttribute( MsvMeshRegulator.aInMesh )
	MsvMeshRegulator.addAttribute( MsvMeshRegulator.aNullMesh )
	MsvMeshRegulator.addAttribute( MsvMeshRegulator.aPassThrough )
	MsvMeshRegulator.addAttribute( MsvMeshRegulator.aOutMeshes )
	MsvMeshRegulator.attributeAffects( MsvMeshRegulator.aInMesh, MsvMeshRegulator.aOutMeshes )
	MsvMeshRegulator.attributeAffects( MsvMeshRegulator.aNullMesh, MsvMeshRegulator.aOutMeshes )
	MsvMeshRegulator.attributeAffects( MsvMeshRegulator.aPassThrough, MsvMeshRegulator.aOutMeshes )

	
