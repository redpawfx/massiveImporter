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

import ns.py as npy
import ns.py.Errors
import ns.py.Timer as Timer

import ns.maya.msv as nmsv
import ns.maya.msv.SceneDescription as SceneDescription
import ns.maya.msv.MasReader as MasReader
from ns.maya.msv.SceneDescription import MsvOpt
import ns.maya.msv.MayaScene as MayaScene
import ns.maya.Progress as Progress

kName = "msvImporter"

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
	
class MsvImporterCmd( OpenMayaMPx.MPxCommand ):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
		self._reset()
		
	def _reset(self):
		self._options = {}
	
	def isUndoable( self ):
		return False
	
	def _parseArgs( self, argData ):		
		self._options[MsvOpt.kLoadSkeleton] = True
		self._options[MsvOpt.kLoadGeometry] = True
		self._options[MsvOpt.kLoadSkin] = True
		self._options[MsvOpt.kLoadPrimitives] = True
		self._options[MsvOpt.kLoadMaterials] = True
		self._options[MsvOpt.kLoadActions] = False
		self._options[MsvOpt.kMaterialType] = "blinn"
		self._options[MsvOpt.kFrameStep] = 1
		self._options[MsvOpt.kInstancePrimitives] = True
		self._options[MsvOpt.kSkinType] = "smooth"
		self._options[MsvOpt.kCacheGeometry] = False
		self._options[MsvOpt.kDeleteSkeleton] = False
		self._options[MsvOpt.kAnimType] = "curves"
				
		if argData.isFlagSet( kSimDirFlag ):
			self._options[MsvOpt.kSimDir] = argData.flagArgumentString( kSimDirFlag, 0 )
		if argData.isFlagSet( kSimTypeFlag ):
			self._options[MsvOpt.kSimType] = argData.flagArgumentString( kSimTypeFlag, 0 )
		if argData.isFlagSet( kMasFileFlag ):
			self._options[MsvOpt.kMasFile] = argData.flagArgumentString( kMasFileFlag, 0 )
		if argData.isFlagSet( kCallsheetFlag ):
			self._options[MsvOpt.kCallsheet] = argData.flagArgumentString( kCallsheetFlag, 0 )
		if argData.isFlagSet( kLoadGeometryFlag ):
			self._options[MsvOpt.kLoadGeometry] = argData.flagArgumentBool( kLoadGeometryFlag, 0 )
			self._options[MsvOpt.kLoadSkin] = argData.flagArgumentBool( kLoadGeometryFlag, 0 )
		if argData.isFlagSet( kSkinTypeFlag ):
			self._options[MsvOpt.kSkinType] = argData.flagArgumentString( kSkinTypeFlag, 0 )
		if argData.isFlagSet( kLoadSegmentsFlag ):
			self._options[MsvOpt.kLoadPrimitives] = argData.flagArgumentBool( kLoadSegmentsFlag, 0 )
		if argData.isFlagSet( kLoadMaterialsFlag ):
			self._options[MsvOpt.kLoadMaterials] = argData.flagArgumentBool( kLoadMaterialsFlag, 0 )
		if argData.isFlagSet( kMaterialTypeFlag ):
			self._options[MsvOpt.kMaterialType] = argData.flagArgumentString( kMaterialTypeFlag, 0 )
		if argData.isFlagSet( kFrameStepFlag ):
			self._options[MsvOpt.kFrameStep] = argData.flagArgumentInt( kFrameStepFlag, 0 )
		if argData.isFlagSet( kInstanceSegmentsFlag ):
			self._options[MsvOpt.kInstancePrimitives] = argData.flagArgumentBool( kInstanceSegmentsFlag, 0 )
		if argData.isFlagSet( kSelectionFlag ):
			selections =[]
			num = argData.numberOfFlagUses( kSelectionFlag )
			for i in range(num):
				args = OpenMaya.MArgList()
				argData.getFlagArgumentList( kSelectionFlag, i, args )
				if args.length():
					selections.append( args.asString(0) )
			self._options[MsvOpt.kSelections] = selections
		if argData.isFlagSet( kCacheGeometryFlag ):
			self._options[MsvOpt.kCacheGeometry] = argData.flagArgumentBool( kCacheGeometryFlag, 0 )
		if argData.isFlagSet( kDeleteSkeletonFlag ):
			self._options[MsvOpt.kDeleteSkeleton] = argData.flagArgumentBool( kDeleteSkeletonFlag, 0 )
		if argData.isFlagSet( kCacheDirFlag ):
			self._options[MsvOpt.kCacheDir] = argData.flagArgumentString( kCacheDirFlag, 0 )
		if argData.isFlagSet( kRangeFlag ):
			self._options[MsvOpt.kRange] = argData.flagArgumentString( kRangeFlag, 0 )
		if argData.isFlagSet( kAnimTypeFlag ):
			self._options[MsvOpt.kAnimType] = argData.flagArgumentString( kAnimTypeFlag, 0 )
			
		if not MsvOpt.kMasFile in self._options:
			raise npy.Errors.BadArgumentError( "The -masFile/-mas flag is required" )
		
		if self._options[MsvOpt.kMaterialType] != "blinn" and \
		   self._options[MsvOpt.kMaterialType] != "lambert":
			raise npy.Errors.BadArgumentError( 'Please choose either "blinn" or "lambert" as the materialType' )

		if self._options[MsvOpt.kSkinType] != "smooth" and \
		   self._options[MsvOpt.kSkinType] != "duplicate" and \
		   self._options[MsvOpt.kSkinType] != "instance":
			raise npy.Errors.BadArgumentError( 'Please choose either "smooth", "duplicate", or "instance" as the skinType' )
		
		if self._options[MsvOpt.kDeleteSkeleton] and \
		   not self._options[MsvOpt.kCacheGeometry]:
			raise npy.Errors.BadArgumentError( 'The skeleton can only be deleted when caching geometry' )

		if self._options[MsvOpt.kCacheGeometry] and \
		   "smooth" != self._options[MsvOpt.kSkinType]:
			self._options[MsvOpt.kCacheGeometry] = False
			self._options[MsvOpt.kDeleteSkeleton] = False
			self.displayWarning( 'Skin type is "%s", geometry will not be cached. Please set skin type to "smooth" to use geometry caching.' % self._options[MsvOpt.kSkinType] )
			
	def doQuery( self, argData ):
		if argData.isFlagSet( kSelectionFlag ):
			if argData.isFlagSet( kMasFileFlag ):
				masFile = argData.flagArgumentString( kMasFileFlag, 0 )
				mas = MasReader.read( masFile )
				self.setResult( mas.selectionGroup.selectionNames() )
			else:
				raise npy.Error.BadArgumentError( "When querying the -selection flag please use the -masFile to indicate which .mas file's selections to query." )
		else:
			raise npy.Error.BadArgumentError( 'Only the -selection flag is queryable.' )
	
	def doIt(self,argList):
		#
		self._reset()
		
		argData = OpenMaya.MArgDatabase( self.syntax(), argList )

		if argData.isQuery():
			self.doQuery( argData )
		else:
			self._parseArgs( argData )
			
			maxRange = 100000
			readProgress = int( 0.25 * maxRange )
			gcProgress = int(0.05 * maxRange)
			buildProgress = maxRange - readProgress - gcProgress
			
			Progress.reset(maxRange)
	
			undoQueue = mc.undoInfo( query=True, state=True )
	
			try:
				try:
					mc.undoInfo( state=False )
					
					Timer.push("TOTAL")
					Progress.setTitle("Reading Files")
					sceneDesc = SceneDescription.SceneDescription(self._options)
					sceneDesc.load( readProgress )
					Progress.setProgress( readProgress )
					
					Progress.setTitle("Creating Maya Data")
					scene = MayaScene.MayaScene()
					scene.build( sceneDesc, buildProgress )
					Progress.setProgress( readProgress + buildProgress )
					Timer.pop()
						
					#for timer in sorted(Timer.names()):
					#	print "%s: %f" % (timer, Timer.elapsed(timer))
					
					Progress.setTitle("Garbage Collecting")
					del sceneDesc
					del scene
					
					gc.collect()
					Progress.setProgress( maxRange )
				finally:
					mc.undoInfo( state=undoQueue )
					Progress.stop()
					Timer.deleteAll()
			except npy.Errors.AbortError:
				self.displayError("Import cancelled by user")
			except:
				raise

		
def creator():
	return OpenMayaMPx.asMPxPtr( MsvImporterCmd() )

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
	
	
	
	
