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

from maya.OpenMaya import *
from maya.OpenMayaMPx import *
import maya.cmds as mc

import ns.py as npy
import ns.py.Errors

import ns.maya.msv.MayaScene as MayaScene
import ns.maya.msv.MayaAgent as MayaAgent
import ns.maya.msv.MayaSkin as MayaSkin
import ns.bridge.data.Scene as Scene
import ns.bridge.io.CDLWriter as CDLWriter

kName = "msvSceneExport"

kFileFlag = "-f"
kFileFlagLong = "-file"

	
class MsvSceneExportCmd( MPxCommand ):
	def __init__(self):
		MPxCommand.__init__(self)
		
	def isUndoable( self ):
		return False
	
	def _parseArgs( self, argData ):		
		
		options = {}
		if argData.isFlagSet(kFileFlag):
			options[kFileFlag] = argData.flagArgumentString( kFileFlag, 0 )
		else:
			raise npy.Errors.BadArgumentError( "The -file/-f flag is required." )
		
		targets = []
		argData.getObjects(targets)
		
		return (options, targets)
						
	def doIt(self,argList):
		argData = MArgDatabase( self.syntax(), argList )

		(options, targets) = self._parseArgs( argData )
		
		undoQueue = mc.undoInfo( query=True, state=True )

		try:
			try:
				mc.undoInfo( state=False )
				
				scene = Scene.Scene()
				
				file = options[kFileFlag]
				ext = os.path.splitext(file)[1]
				if ext == ".mas":
					raise npy.Errors.BadArgumentError( "Exporting to a .mas file is not yet supported." )
				elif ext == ".cdl":
					pass
				else:
					raise npy.Errors.BadArgumentError( "Please provide a Massive setup (.mas) or agent (.cdl) file." )
				
				fileHandle = open(file, "w")
				
				scene = Scene.Scene()
				MayaScene.dump(scene, targets[0])
				if scene.agentSpecs():
					CDLWriter.write(fileHandle, scene.agentSpecs()[0])
				
			finally:
				mc.undoInfo( state=undoQueue )
		except npy.Errors.AbortError:
			self.displayError("Export cancelled by user")
		except:
			raise

		
def creator():
	return asMPxPtr( MsvSceneExportCmd() )

def syntaxCreator():
	syntax = MSyntax()
	syntax.addFlag( kFileFlag, kFileFlagLong, MSyntax.kString )
	
	syntax.setObjectType(MSyntax.kStringObjects, 1, 1)
	syntax.useSelectionAsDefault(True)
	
	return syntax
	
	
	
	
