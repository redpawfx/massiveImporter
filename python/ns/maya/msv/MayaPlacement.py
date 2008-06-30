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

import maya.cmds as mc
import maya.mel
from maya.OpenMaya import *

import ns.py
import ns.py.Errors as Errors
import ns.py.Timer as Timer
import ns.maya.Progress as Progress

import ns.maya.msv
import ns.maya.msv.MasDescription as MasDescription
import ns.maya.msv.MasWriter as MasWriter
import ns.maya.msv.MasReader as MasReader

def build( fileHandle ):
	'''Given a text stream in the format of a .mas file, build the described
	   Massive setup using Maya objects. For now only locators are supported.
	'''
	mas = MasReader.read(fileHandle)
	
	# "massive" partition contains one set per Massive group. Each set
	# member corresponds to a Massive locator. By default Maya locators
	# are used.
	if not mc.objExists("massive"):
		# The "massive" partition must exist
		mc.partition(name="massive")
	elif "partition" != mc.nodeType("massive"):
		# For now we bail if the user has a non-partition node called
		# "massive"
		raise Errors.Error("An object named 'massive' already exists and is not a partition. Please rename it.")
	
	# List of Maya objects representing locators, indexed by the
	# id of their group. These objects will be updated by incoming
	# massive data - once the number of incoming massive locators
	# exceeds the number of pre-existing Maya locators, new Maya
	# locators are created. Newly created locators are not added
	# to this list.
	mayaGroupLocators = []
	# Number of locators in each mayaGroup, used to determine whether
	# an incoming massive locator can just update an existing Maya
	# locator or whether it will cause a new Maya locator to be created.
	# This number starts at 0 and is incremented whenver a Maya locator
	# is updated or created.
	mayaGroupCounts = []
	for g in mas.groups:
		if mc.objExists(g.name):
			# For now we bail if the user has a non-set node which
			# has a name class with in incoming massive group
			if "objectSet" != mc.nodeType(g.name):
				raise Errors.Error("Attempting to sync a group called %s from " +
								   "Massive, but an object by that name " +
								   "already exists and is not a set. " +
								   "Please rename it." % g.name)
		else:
			# Create a Maya set to represent the incoming Massive
			# group.
			mc.sets(empty=True, name=g.name)
			mc.partition(g.name, add="massive")
		# Initialize mayaGroupLocators with the pre-existing set
		# members.
		locators = mc.sets(g.name, query=True)
		if not locators:
			# 'sets' command returns None instead of [] if the set is empty
			locators = []
		mayaGroupLocators.append( locators )
		mayaGroupCounts.append(0)
	
	updated = 0
	created = 0
	for i in range(len(mas.locators)):
		locator = mas.locators[i]
		groupId = locator.group
		mayaGroup = mas.groups[groupId].name
		if not mayaGroup:
			continue
		mayaLocators = mayaGroupLocators[groupId]
		if mayaGroupCounts[groupId] < len(mayaLocators):
			# Maya locator exists, update it
			mayaLocator = mayaLocators[mayaGroupCounts[groupId]]
			updated += 1
		else:
			# The number of incoming massive locators exceeds
			# the number of pre-existing Maya locators, create
			# a new Maya locator
			mayaLocator = mc.spaceLocator()
			mc.sets(mayaLocator, add=mayaGroup)
			created += 1
		mayaGroupCounts[groupId] += 1
		# Update the position of the Maya locator
		mc.xform(mayaLocator, worldSpace=True, translation=locator.position)
	print >> sys.stderr, "Created %d locators" % created
	print >> sys.stderr, "Updated %d locators" % updated

def dump( fileHandle ):
	'''Look through the Maya scene and dump to fileHandle, in .mas format,
	   any Maya objects that represent Massive entitities. For now only
	   Massive groups and locators are supported.'''
	if ( not mc.objExists( "massive" ) or
		 "partition" != mc.nodeType( "massive" ) ):
		# Massive groups are represented by Maya sets of the same
		# name stored in the "massive" partition. If no "massive" partition
		# exists, bail.
		raise ns.py.Error("Scene does not contain any Massive locators.")

	# Get a list of all Massive groups
	groups = mc.partition( "massive", query=True )
	# This MasDescription object will be populated with the Massive
	# setup data and written to 'fileHandle'
	mas = MasDescription.MasDescription()

	groupId = 0
	for group in groups:
		mas.groups.append( MasDescription.Group( groupId, group ) )
		# Get all the Massive locators in 'group'
		locators = mc.sets( group, query=True )
		for locator in locators:
			# Get the locator world space position
			position = mc.xform( locator,
								 query=True,
								 translation=True,
								 worldSpace=True )
			mas.locators.append( MasDescription.Locator( groupId, position ) )
		groupId += 1
		
	# Write the Massive setup information to 'fileHandle'
	MasWriter.write( fileHandle, mas )
