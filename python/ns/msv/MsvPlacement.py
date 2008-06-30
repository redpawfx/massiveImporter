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

import ns.py
import ns.py.Errors
import ns.py.Timer as Timer

import ns.maya.msv.MasDescription as MasDescription
import ns.maya.msv.MasWriter as MasWriter

import massive

def build( mas ):
	'''Given a MasDescription object describing a Massive setup, updated and
	   create the described Massive entities. For now only locators are supported.
	'''
	# List of Massive Group objects
	msvGroups = []
	# Counter used to keep track of the number of locators updated
	# in the corresponding Massive Group. If this number is greater
	# than or equal to Group.n_locator, we need to create a new
	# Locator, otherwise we can just update an existing Locator.
	msvGroupCounts = []
	# Find Massive Groups for each of the group mentioned
	for g in mas.groups:
		if g.id >= len(msvGroups):
			msvGroups.extend([ None ] * (g.id - len(msvGroups) + 1))
		msvGroups[g.id] = massive.find_group(g.name)
		msvGroupCounts.append(0)
	
	updated = 0
	created = 0
	for locator in mas.locators:
		msvGroup = msvGroups[locator.group]
		if not msvGroup:
			continue
		locatorId = msvGroupCounts[locator.group]
		if locatorId < msvGroup.n_locator:
			# Update the corresponding Locator
			updated += 1
			msvLocator = msvGroup.get_locator(locatorId)
		else:
			# Create a new Locator
			created += 1
			msvLocator = msvGroup.add_locator()
		msvGroupCounts[locator.group] += 1
		msvLocator.px = locator.position[0]
		msvLocator.py = locator.position[1]
		msvLocator.pz = locator.position[2]
		
	# Refresh the view port
	massive.redraw_view()
	print >> sys.stderr, "Created %d locators" % created
	print >> sys.stderr, "Updated %d locators" % updated

def dump( fileHandle, groups ):
	'''Look through the Massive scene and dump to fileHandle, in .mas format,
	   all of the Groups specified by 'groups' as well as their Locators.
	'''
	# The MasDescription object is an intermediary data format
	# which MasWriter/MasReader write from and read to
	mas = MasDescription.MasDescription()
	for name in groups:
		# Find the named Massive Group
		group = massive.find_group(name)
		if not group:
			continue
		id = len(mas.groups)
		mas.groups.append(MasDescription.Group(id, name))
		
		# Add each of the Group's locators to the MasDescription
		for i in range(group.n_locator):
			locator = group.get_locator(i)
			position = (locator.px, locator.py, locator.pz)
			mas.locators.append(MasDescription.Locator(id, position))
	# Dump the data to fileHandle
	MasWriter.write(fileHandle, mas)
