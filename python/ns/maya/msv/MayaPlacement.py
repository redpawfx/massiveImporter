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

def getGroupsSet(create=False):
	'''The groups set is a set which contains all of the sets representing
	   massive groups.'''
	# "massive_groups" set contains one set per Massive group. Each set
	# member corresponds to a Massive locator. By default Maya locators
	# are used.
	groupsSet = "massive_groups"
	if not mc.objExists(groupsSet):
		if create:
			# The "massive_grups" partition must exist
			groupsSet = mc.sets(name=groupsSet, empty=True)
			mc.addAttr(groupsSet, longName="massive", attributeType="long")
		else:
			raise Errors.Error("Scene does not contain any Massive groups.")
	elif "objectSet" != mc.nodeType(groupsSet):
		# For now we bail if the user has a non-partition node called
		# "massive_groups"
		raise Errors.Error("An object named '%s' already exists and is not a set. Please rename it." % groupsSet)
	
	return groupsSet;

def isGroupsSet(set):
	return ("objectSet" == mc.nodeType(set) and
			"massive_groups" == set)

def createGroup(group, force):
	if not force and mc.objExists(group):
		# For now we bail if the user has a non-set node which
		# has a name class with in incoming massive group
		if "objectSet" != mc.nodeType(group):
			raise Errors.Error("Attempting to sync a group called %s from " +
							   "Massive, but an object by that name " +
							   "already exists and is not a set. " +
							   "Please rename it." % group)
	else:
		# Create a Maya set to represent the incoming Massive
		# group.
		group = mc.sets(empty=True, name=group)
		mc.addAttr(group, longName="massive", attributeType="long")
		mc.sets(group, add=getGroupsSet(True))
		
def addLocators(group="", locators=[]):
	if not group and not locators:
		selection = mc.ls(sl=True)
		if len(selection) < 2:
			raise Errors.BadArgumentError("Please select some objects to turn into Massive locators, and a massive group.")
		group = selection[-1]
		locators = selection[0:-1]
		addLocators(group, locators)
	else:
		if not group or not locators:
			raise Errors.BadArgumentError("Please select some objects to turn into Massive locators, and a massive group.")
		if not isGroup(group):
			raise Errors.BadArgumentError("%s is not a massive group." % group)
		if isGroupsSet(group):
			raise Errors.BadArgumentError("%s can not have locators added to it." % group)
		for locator in locators:
			try:
				mc.xform(locator, query=True, worldSpace=True, translation=True)
			except:
				raise Errors.BadArgumentError("%s can not be turned into a Massive locator.\n" +
											  "Please select items whose transformation is accessible through the 'xform' command." % locator)
			if not mc.objExists("%s.massive" % locator):
				mc.addAttr(locator, longName="massive", attributeType="long")
		mc.sets(locators, add=group)
		
def removeLocators(locators=[]):
	if not locators:
		selection = mc.ls(sl=True)
		if not selection:
			return
		removeLocators(selection)
	else:
		for locator in locators:
			sets = mc.listSets(object=locator)
			for set in sets:
				if isGroup(set):
					mc.sets(locator, edit=True, rm=set)
			mc.deleteAttr("%s.massive" % locator)		
		

def isGroup(group):
	return ("objectSet" == mc.nodeType(group) and
			mc.objExists("%s.massive" % group))

def build( fileHandle ):
	'''Given a text stream in the format of a .mas file, build the described
	   Massive setup using Maya objects. For now only locators are supported.
	'''
	mas = MasReader.read(fileHandle)
	
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
		createGroup(g.name, force=False)
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
			addLocators(mayaGroup, mayaLocator)
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
	# Massive groups are represented by Maya sets of the same
	# name stored in the "massive_groups" set. If no "massive_groups" set
	# exists, bail.
	groupsSet = getGroupsSet(False)

	# Get a list of all Massive groups
	groups = mc.sets( groupsSet, query=True )
	if not groups:
		groups = []
	# This MasDescription object will be populated with the Massive
	# setup data and written to 'fileHandle'
	mas = MasDescription.MasDescription()

	groupId = 0
	for group in groups:
		mas.groups.append( MasDescription.Group( groupId, group ) )
		# Get all the Massive locators in 'group'
		locators = mc.sets( group, query=True )
		if not locators:
			locators = []
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
