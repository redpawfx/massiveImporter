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

import ns.maya.msv as nmsv
import ns.bridge.io.MasReader as MasReader
import ns.maya.msv.MayaPlacement as MayaPlacement
from ns.bridge.data.SimManager import MsvOpt

kName = "msvSceneImport"

kMasFileFlag = "-mas"
kMasFileFlagLong = "-masFile"
kCdlFileFlag = "-cdl"
kCdlFileFlagLong = "-cdlFile"
	
class MsvSceneImportCmd( OpenMayaMPx.MPxCommand ):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
		self._reset()
		
	def _reset(self):
		self._options = {}
	
	def isUndoable( self ):
		return False
	
	def _parseArgs( self, argData ):		

		if argData.isFlagSet( kMasFileFlag ):
			self._options[MsvOpt.kMasFile] = argData.flagArgumentString( kMasFileFlag, 0 )
		if argData.isFlagSet( kCdlFileFlag ):
			self._options[MsvOpt.kCdlFile] = argData.flagArgumentString( kCdlFileFlag, 0 )
						
		if (not MsvOpt.kMasFile in self._options and
		    not MsvOpt.kCdlFile in self._options):
			raise npy.Errors.BadArgumentError( "The -masFile/-mas or -cdlFile/-cdl flag is required" )
		if (MsvOpt.kMasFile in self._options and
		    MsvOpt.kCdlFile in self._options):
			raise npy.Errors.BadArgumentError( "The -masFile/-mas and -cdlFile/-cdl flags are mutually exclusive" )
		
						
	def doIt(self,argList):
		self._reset()
		
		argData = OpenMaya.MArgDatabase( self.syntax(), argList )

		self._parseArgs( argData )
		
		undoQueue = mc.undoInfo( query=True, state=True )

		try:
			try:
				mc.undoInfo( state=False )
				
				if MsvOpt.kMasFile in self._options:				
					masHandle = open(self._options[MsvOpt.kMasFile], "r")
					mas = MasReader.read(masHandle)
					MayaPlacement.build(mas)
				elif MsvOpt.kCdlFile in self._options:
					cdlReader = CDLReader.CDLReader()
					agentSpec = cdlReader.read( self._options[MsvOpt.kCdlFile] )
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
	syntax.addFlag( kMasFileFlag, kMasFileFlagLong, OpenMaya.MSyntax.kString )
	syntax.addFlag( kCdlFileFlag, kCdlFileFlagLong, OpenMaya.MSyntax.kString )
	
	return syntax
	
	
	
	
