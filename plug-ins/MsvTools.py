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

import os
import os.path
import sys
import maya.OpenMayaMPx as OpenMayaMPx

importer = None

# initialize the script plug-in
def initializePlugin(oPlugin):
	fPlugin = OpenMayaMPx.MFnPlugin(oPlugin)
	
	# Find the python source and add it to the pythonpath. This
	# assumes that this file (MsvTools.py) lives in the 'plug-ins'
	# directory which is a sibling of the 'python' directory containing
	# the python source. This should be the case if the plug-in was
	# installed following the directions in the included INSTALL.txt
	# file.
	#
	installPath = "%s/.." % fPlugin.loadPath()
	pyPath = "%s/python" % installPath
	nsPath = "%s/ns" % pyPath
	if not os.path.isdir(pyPath) or not os.path.isdir(nsPath):
		sys.stderr.write( "Error loading plugin: MsvTools python source was not found in %s\n" % pyPath )
		raise
	sys.path.append( pyPath )
	
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
	global importer
	importer = RollbackImporter.RollbackImporter("OpenMaya")
	
	import ns.maya.msv.MsvSimImportCmd as MsvSimImportCmd
	import ns.maya.msv.MsvSimLoader as MsvSimLoader
	
	try:
		fPlugin.registerCommand( MsvSimImportCmd.kName,
								 MsvSimImportCmd.creator,
								 MsvSimImportCmd.syntaxCreator )
	except:
		sys.stderr.write( "Failed to register command: %s" % MsvSimImportCmd.kName )
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
	
	import ns.maya.msv.MsvSimImportCmd as MsvSimImportCmd
	import ns.maya.msv.MsvSimLoader as MsvSimLoader

	try:
		fPlugin.deregisterCommand( MsvSimImportCmd.kName )
	except:
		sys.stderr.write( "Failed to deregister command: %s" % MsvSimImportCmd.kName )
		raise
	
	try:
		fPlugin.deregisterNode( MsvSimLoader.kId )
	except:
		sys.stderr.write( "Failed to deregister node: %s" % MsvSimLoader.kName )
		raise

	# Unload all modules.
	#
	global importer
	if importer:
		importer.uninstall()
	