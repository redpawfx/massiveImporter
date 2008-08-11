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
import gc

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as mc

import ns.py as npy
import ns.py.Errors

import ns.maya.msv.MayaScene as MayaScene
import ns.maya.msv.MayaAgent as MayaAgent
import ns.maya.msv.MayaSkin as MayaSkin
import ns.bridge.data.Scene as Scene

kName = "msvSceneImport"

kFileFlag = "-f"
kFileFlagLong = "-file"
kLoadGeometryFlag = "-lg"
kLoadGeometryFlagLong = "-loadGeometry"
kSkinTypeFlag = "-skt"
kSkinTypeFlagLong = "-skinType"
kLoadSegmentsFlag = "-ls"
kLoadSegmentsFlagLong = "-loadSegments"
kLoadMaterialsFlag = "-lm"
kLoadMaterialsFlagLong = "-loadMaterials"
kMaterialTypeFlag = "-mt"
kMaterialTypeFlagLong = "-materialType"
kInstanceSegmentsFlag = "-is"
kInstanceSegmentsFlagLong = "-instanceSegments"

	
class MsvSceneImportCmd( OpenMayaMPx.MPxCommand ):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
		
	def isUndoable( self ):
		return False
	
	def _parseArgs( self, argData ):		
		
		options = {}
		if argData.isFlagSet(kFileFlag):
			options[kFileFlag] = argData.flagArgumentString( kFileFlag, 0 )
		else:
			raise npy.Errors.BadArgumentError( "The -file/-f flag is required." )
		
		if argData.isFlagSet(kLoadGeometryFlag):
			options[kLoadGeometryFlag] = argData.flagArgumentBool(kLoadGeometryFlag, 0)
		else:
			options[kLoadGeometryFlag] = True
			
		if argData.isFlagSet( kSkinTypeFlag ):
			str = argData.flagArgumentString( kSkinTypeFlag, 0 )
			if (str == "smooth"):
				options[kSkinTypeFlag] = MayaSkin.eSkinType.smooth
			elif (str == "duplicate"):
				options[kSkinTypeFlag] = MayaSkin.eSkinType.duplicate
			elif (str == "instance"):
				options[kSkinTypeFlag] = MayaSkin.eSkinType.instance
			else:
				raise ns.py.Errors.BadArgumentError( 'Please choose either "smooth", "duplicate", or "instance" as the skinType' )
		else:
			options[kSkinTypeFlag] = MayaSkin.eSkinType.smooth

		if argData.isFlagSet( kLoadSegmentsFlag ):
			options[kLoadSegmentsFlag] = argData.flagArgumentBool( kLoadSegmentsFlag, 0 )
		else:
			options[kLoadSegmentsFlag] = False
			
		if argData.isFlagSet( kLoadMaterialsFlag ):
			options[kLoadMaterialsFlag] = argData.flagArgumentBool( kLoadMaterialsFlag, 0 )
		else:
			options[kLoadMaterialsFlag] = True
			
		if argData.isFlagSet(kMaterialTypeFlag):
			options[kMaterialTypeFlag] = argData.flagArgumentString(kMaterialTypeFlag, 0)
		else:
			options[kMaterialTypeFlag] = "blinn"

		if argData.isFlagSet( kInstanceSegmentsFlag ):
			options[kInstanceSegmentsFlag] = argData.flagArgumentBool( kInstanceSegmentsFlag, 0 )
		else:
			options[kInstanceSegmentsFlag] = True

		return options
						
	def doIt(self,argList):
		argData = OpenMaya.MArgDatabase( self.syntax(), argList )

		options = self._parseArgs( argData )
		
		undoQueue = mc.undoInfo( query=True, state=True )

		try:
			try:
				mc.undoInfo( state=False )
				
				scene = Scene.Scene()
				
				file = options[kFileFlag]
				ext = os.path.splitext(file)[1]
				if ext == ".mas":
					scene.setMas(file)
				elif ext == ".cdl":
					scene.addCdl(file)
				else:
					raise npy.Errors.BadArgumentError( "Please provide a Massive setup (.mas) or agent (.cdl) file." )
				
				agentOptions = MayaAgent.Options()
				agentOptions.loadGeometry = options[kLoadGeometryFlag]
				agentOptions.loadPrimitives = options[kLoadSegmentsFlag]
				agentOptions.loadMaterials = options[kLoadMaterialsFlag]
				agentOptions.skinType = options[kSkinTypeFlag]
				agentOptions.instancePrimitives = options[kInstanceSegmentsFlag]
				agentOptions.materialType = options[kMaterialTypeFlag]
				
				mayaScene = MayaScene.MayaScene()
				mayaScene.build(scene, agentOptions)
			finally:
				mc.undoInfo( state=undoQueue )
		except npy.Errors.AbortError:
			self.displayError("Import cancelled by user")
		except:
			raise

		
def creator():
	return OpenMayaMPx.asMPxPtr( MsvSceneImportCmd() )

def syntaxCreator():
	syntax = OpenMaya.MSyntax()
	syntax.addFlag( kFileFlag, kFileFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kLoadGeometryFlag, kLoadGeometryFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kSkinTypeFlag, kSkinTypeFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kLoadSegmentsFlag, kLoadSegmentsFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kLoadMaterialsFlag, kLoadMaterialsFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kMaterialTypeFlag, kMaterialTypeFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kInstanceSegmentsFlag, kInstanceSegmentsFlagLong, OpenMaya.MSyntax.kBoolean )

	return syntax
	
	
	
	
