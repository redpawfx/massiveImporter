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
import gc

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as mc

import ns.py
import ns.py.Errors

import ns.maya.msv
import ns.bridge.io.MasReader as MasReader
import ns.bridge.data.Scene as Scene
import ns.bridge.data.Sim as Sim
import ns.maya.msv.MayaSkin as MayaSkin
import ns.maya.msv.MayaSim as MayaSim
import ns.maya.msv.MayaAgent as MayaAgent
import ns.maya.msv.MayaSimAgent as MayaSimAgent

kName = "msvSimImport"

kSimDirFlag = "-sd"
kSimDirFlagLong = "-simDir"
kSimTypeFlag = "-st"
kSimTypeFlagLong = "-simType"
kMasFileFlag = "-mas"
kMasFileFlagLong = "-masFile"
kCallsheetFlag = "-cal"
kCallsheetFlagLong = "-callsheet"
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
kFrameStepFlag = "-fs"
kFrameStepFlagLong = "-frameStep"
kInstanceSegmentsFlag = "-is"
kInstanceSegmentsFlagLong = "-instanceSegments"
kSelectionFlag = "-sel"
kSelectionFlagLong = "-selection"
kCacheGeometryFlag = "-cg"
kCacheGeometryFlagLong = "-cacheGeometry"
kDeleteSkeletonFlag = "-ds"
kDeleteSkeletonFlagLong = "-deleteSkeleton"
kCacheDirFlag = "-cd"
kCacheDirFlagLong = "-cacheDir"
kRangeFlag = "-r"
kRangeFlagLong = "-range"
kAnimTypeFlag = "-at"
kAnimTypeFlagLong = "-animType"
	
class MsvSimImportCmd( OpenMayaMPx.MPxCommand ):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
		
	def isUndoable( self ):
		return False
	
	def _parseArgs( self, argData ):		
		options = {}	
		if argData.isFlagSet(kSimDirFlag):
			options[kSimDirFlag] = argData.flagArgumentString(kSimDirFlag, 0 )
		else:
			options[kSimDirFlag] = ""
			
		if argData.isFlagSet(kSimTypeFlag):
			options[kSimTypeFlag] = ".%s" % argData.flagArgumentString(kSimTypeFlag, 0)
		else:
			options[kSimTypeFlag] = ".amc"
			
		if argData.isFlagSet(kMasFileFlag):
			options[kMasFileFlag] = argData.flagArgumentString(kMasFileFlag, 0)
		else:
			raise ns.py.Errors.BadArgumentError("The %s/%s flag is required" % (kMasFileFlagLong, kMasFileFlag)) 
		
		if argData.isFlagSet(kCallsheetFlag):
			options[kCallsheetFlag] = argData.flagArgumentString(kCallsheetFlag, 0)
		else:
			options[kCallsheetFlag] = ""
			
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
			
		if argData.isFlagSet( kFrameStepFlag ):
			options[kFrameStepFlag] = argData.flagArgumentInt( kFrameStepFlag, 0 )
		else:
			options[kFrameStepFlag] = 1
			
		if argData.isFlagSet( kInstanceSegmentsFlag ):
			options[kInstanceSegmentsFlag] = argData.flagArgumentBool( kInstanceSegmentsFlag, 0 )
		else:
			options[kInstanceSegmentsFlag] = True
			
		if argData.isFlagSet( kSelectionFlag ):
			selections =[]
			num = argData.numberOfFlagUses( kSelectionFlag )
			for i in range(num):
				args = OpenMaya.MArgList()
				argData.getFlagArgumentList( kSelectionFlag, i, args )
				if args.length():
					selections.append( args.asString(0) )
			options[kSelectionFlag] = selections
		else:
			options[kSelectionFlag] = []
			
		if argData.isFlagSet( kCacheGeometryFlag ):
			options[kCacheGeometryFlag] = argData.flagArgumentBool( kCacheGeometryFlag, 0 )
		else:
			options[kCacheGeometryFlag] = False
			
		if argData.isFlagSet( kDeleteSkeletonFlag ):
			options[kDeleteSkeletonFlag] = argData.flagArgumentBool( kDeleteSkeletonFlag, 0 )
		else:
			options[kDeleteSkeletonFlag] = False
			
		if argData.isFlagSet( kCacheDirFlag ):
			options[kCacheDirFlag] = argData.flagArgumentString( kCacheDirFlag, 0 )
		else:
			options[kCacheDirFlag] = ""
			
		if argData.isFlagSet( kRangeFlag ):
			options[kRangeFlag] = argData.flagArgumentString( kRangeFlag, 0 )
		else:
			options[kRangeFlag] = ""
			
		if argData.isFlagSet( kAnimTypeFlag ):
			str = argData.flagArgumentString( kAnimTypeFlag, 0 )
			if (str == "curves"):
				options[kAnimTypeFlag] = MayaSimAgent.eAnimType.curves
			elif (str == "loader"):
				options[kAnimTypeFlag] = MayaSimAgent.eAnimType.loader
			else:
				raise ns.py.Errors.BadArgumentError( 'Please choose either "curves" or "loader" as the animType' )
		else:
			options[kAnimTypeFlag] = MayaSimAgent.eAnimType.curves
					
		if ( options[kMaterialTypeFlag] != "blinn" and
		     options[kMaterialTypeFlag] != "lambert" ):
			raise ns.py.Errors.BadArgumentError( 'Please choose either "blinn" or "lambert" as the materialType' )

		if (options[kDeleteSkeletonFlag] and not options[kCacheGeometryFlag]):
			raise ns.py.Errors.BadArgumentError( 'The skeleton can only be deleted when caching geometry' )

		if ( options[kCacheGeometryFlag] and
		     MayaSkin.eSkinType.smooth != options[kSkinTypeFlag] ):
			options[kCacheGeometryFlag] = False
			options[kDeleteSkeletonFlag] = False
			self.displayWarning( 'Skin type is "%s", geometry will not be cached. Please set skin type to "smooth" to use geometry caching.' % self._options[MsvOpt.kSkinType] )
	
		return options
			
	def doQuery( self, argData ):
		if argData.isFlagSet( kSelectionFlag ):
			if argData.isFlagSet( kMasFileFlag ):
				masFile = argData.flagArgumentString( kMasFileFlag, 0 )
				fileHandle = open(masFile, "r")
				try:
					mas = MasReader.read( fileHandle )
				finally:
					fileHandle.close()
				self.setResult( mas.selectionGroup.selectionNames() )
			else:
				raise ns.py.Error.BadArgumentError( "When querying the -selection flag please use the -masFile to indicate which .mas file's selections to query." )
		else:
			raise ns.py.Error.BadArgumentError( 'Only the -selection flag is queryable.' )
	
	def doIt(self,argList):
		argData = OpenMaya.MArgDatabase( self.syntax(), argList )

		if argData.isQuery():
			self.doQuery( argData )
		else:
			options = self._parseArgs( argData )
			
			undoQueue = mc.undoInfo( query=True, state=True )
	
			try:
				try:
					mc.undoInfo( state=False )
					
					scene = Scene.Scene()
					scene.setMas(options[kMasFileFlag])
					
					sim = Sim.Sim(scene,
								  options[kSimDirFlag],
								  options[kSimTypeFlag],
								  options[kCallsheetFlag],
								  options[kSelectionFlag],
								  options[kRangeFlag])
				
					agentOptions = MayaAgent.Options()
					agentOptions.loadGeometry = options[kLoadGeometryFlag]
					agentOptions.loadPrimitives = options[kLoadSegmentsFlag]
					agentOptions.loadMaterials = options[kLoadMaterialsFlag]
					agentOptions.skinType = options[kSkinTypeFlag]
					agentOptions.instancePrimitives = options[kInstanceSegmentsFlag]
					agentOptions.materialType = options[kMaterialTypeFlag]
						
					mayaSim = MayaSim.MayaSim()
					mayaSim.build(sim,
								  options[kAnimTypeFlag],
								  options[kFrameStepFlag],
								  options[kCacheGeometryFlag],
								  options[kCacheDirFlag],
								  options[kDeleteSkeletonFlag],
								  agentOptions)
					del mayaSim
					del sim
					del scene
					
					gc.collect()
				finally:
					mc.undoInfo( state=undoQueue )
			except ns.py.Errors.AbortError:
				self.displayError("Import cancelled by user")
			except:
				raise

		
def creator():
	return OpenMayaMPx.asMPxPtr( MsvSimImportCmd() )

def syntaxCreator():
	syntax = OpenMaya.MSyntax()
	syntax.addFlag( kSimDirFlag, kSimDirFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kSimTypeFlag, kSimTypeFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kMasFileFlag, kMasFileFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kCallsheetFlag, kCallsheetFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kLoadGeometryFlag, kLoadGeometryFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kSkinTypeFlag, kSkinTypeFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kLoadSegmentsFlag, kLoadSegmentsFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kLoadMaterialsFlag, kLoadMaterialsFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kMaterialTypeFlag, kMaterialTypeFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kFrameStepFlag, kFrameStepFlagLong, OpenMaya.MSyntax.kLong )
	syntax.addFlag( kInstanceSegmentsFlag, kInstanceSegmentsFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kSelectionFlag, kSelectionFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kCacheGeometryFlag, kCacheGeometryFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kDeleteSkeletonFlag, kDeleteSkeletonFlagLong, OpenMaya.MSyntax.kBoolean )
	syntax.addFlag( kCacheDirFlag, kCacheDirFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kRangeFlag, kRangeFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kAnimTypeFlag, kAnimTypeFlagLong, OpenMaya.MSyntax.kString )
	
	syntax.makeFlagMultiUse( kSelectionFlag )
	
	syntax.makeFlagQueryWithFullArgs( kMasFileFlag, False )
	
	syntax.enableQuery( True )
	
	return syntax
	
	
	
	
