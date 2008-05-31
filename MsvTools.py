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
import maya.OpenMayaMPx as OpenMayaMPx

from ns.py import RollbackImporter

# Any modules imported after the RollbackImporter is instantiated
# will be unloaded when the plugin is unloaded. This guarantees
# that when the plug-in is reloaded, all modules will be reloaded
# as well. This helps during development as it is not
# necessary to restart maya for python changes to take effect.
#
# Passing in "OpenMaya" tells the RollbackImporter to ignore the
# OpenMaya* modules.
#
importer = RollbackImporter.RollbackImporter("OpenMaya")

import ns.maya.msv.MsvImporterCmd as MsvImporterCmd
import ns.maya.msv.MsvMeshRegulator as MsvMeshRegulator
import ns.maya.msv.MsvSimLoader as MsvSimLoader

# initialize the script plug-in
def initializePlugin(oPlugin):
	fPlugin = OpenMayaMPx.MFnPlugin(oPlugin)
	try:
		fPlugin.registerCommand( MsvImporterCmd.kName,
								 MsvImporterCmd.creator,
								 MsvImporterCmd.syntaxCreator )
	except:
		sys.stderr.write( "Failed to register command: %s" % MsvImporterCmd.kName )
		raise
	
	try:
		fPlugin.registerNode( MsvMeshRegulator.kName,
							  MsvMeshRegulator.kId,
							  MsvMeshRegulator.nodeCreator,
							  MsvMeshRegulator.nodeInitializer )
	except:
		sys.stderr.write( "Failed to register node: %s" % MsvMeshRegulator.kName )
		raise
	
	try:
		fPlugin.registerNode( MsvSimLoader.kName,
							  MsvSimLoader.kId,
							  MsvSimLoader.nodeCreator,
							  MsvSimLoader.nodeInitializer )
	except:
		sys.stderr.write( "Failed to register node: %s" % MsvSimLoader.kName )
		raise



# uninitialize the script plug-in
def uninitializePlugin(oPlugin):
	fPlugin = OpenMayaMPx.MFnPlugin(oPlugin)
	try:
		fPlugin.deregisterCommand( MsvImporterCmd.kName )
	except:
		sys.stderr.write( "Failed to deregister command: %s" % MsvImporterCmd.kName )
		raise
	   
	try:
		fPlugin.deregisterNode( MsvMeshRegulator.kId )
	except:
		sys.stderr.write( "Failed to deregister node: %s" % MsvMeshRegulator.kName )
		raise
	
	try:
		fPlugin.deregisterNode( MsvSimLoader.kId )
	except:
		sys.stderr.write( "Failed to deregister node: %s" % MsvSimLoader.kName )
		raise

	# Unload all modules.
	#
	global importer
	importer.uninstall()
	