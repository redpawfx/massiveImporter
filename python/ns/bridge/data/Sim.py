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

import ns
import ns.py as nsp
import ns.py.Errors
import ns.bridge.data.AgentDescription as AgentDescription

class Sim:	
	def __init__(self, selectionGroup=None):
		self._agents = {}
		self._selectionGroup = selectionGroup
		
	def agent(self, name):
		'''Return the sim data for agent 'name'. A new Sim.Agent object will
		   be created if necessary. If a selection group was provided when
		   initializing the Sim, check that the specified agent is in the
		   selection.'''
		if self._selectionGroup:
			id = int(name.split("_")[-1])
			if not self._selectionGroup.contains( id ):
				# Filter out non-selected agents
				#
				return None
		
		a = None
		try:
			a = self._agents[name]
		except:
			a = Agent(name)
			self._agents[name] = a
		return a
	
	def agents(self):
		return self._agents.values()
	   
class Agent:
	def __init__(self, name):
		self._name = name
		self._joints = {}
		self.startFrame = -sys.maxint
		self.endFrame = -sys.maxint
	
	def name(self):
		return self._name
	
	def joints(self):
		return self._joints.values()
	
	def joint(self, jointName):
		return self._joints[jointName]
	
	def addSample(self, jointName, frame, data):
		if -sys.maxint == self.startFrame or frame < self.startFrame:
				self.startFrame = frame
		if -sys.maxint == self.endFrame or frame > self.endFrame:
				self.endFrame = frame
			
		j = None
		try:
			j = self._joints[jointName]
		except:
			j = Joint(jointName, frame)
			self._joints[jointName] = j
		j.addSample(frame, data)
		
	def prune(self, jointNames):
		'''Delete any joints not listed in jointNames'''
		s = frozenset(jointNames)
		for j in self._joints.keys():
			if not j in s:
				del self._joints[j]
	
class Joint:
	def __init__(self, name, startFrame):
		# Each entry in _channels will contain a list of values for that
		# channel, one value per frame
		self._channels = []
		self._startFrame = startFrame
		self._numFrames = 0
		self._numChannels = 0
		self._name = name
		self._order = {}
		
	def name(self):
		return self._name
	
	def startFrame(self):
		return self._startFrame
	
	def numFrames(self):
		return self._numFrames
	
	def numChannels(self):
		return self._numChannels
	
	def channelNames(self):
		return self._order.keys()
	
	def setOrderDOF(self, order, dof):
		'''Map channel names to the indices in the _channels array.'''
		i = 0
		for channel in range(len(order)):
			if not dof[channel]:
				continue
			channelName = AgentDescription.enum2Channel[order[channel]]
			self._order[channelName] = i
			i += 1
		
	def sample(self, channelName, frame):
		'''Return the sample value for 'channelName' at frame 'frame'. If we
		   don't have any data for 'channelName' return 0.0.'''
		sample = 0.0
		try:
			channel = self._channels[self._order[channelName]]
			sample = channel[self._index(frame)]
		finally:
			return sample
		
	def sampleByIndex(self, index, frame):
		sample = 0.0
		try:
			channel = self._channels[index]
			sample = channel[self._index(frame)]
		finally:
			return sample
		
	def addSample(self, frame, data):
		'''Add one frame's worth of data. data contains one sample per channel.
		'''
		
		if not self._numFrames:
			# First sample added determins the number of channels for this
			# Joint.
			self._numChannels = len(data)
			for i in range(self._numChannels):
				self._channels.append([])
		elif len(data) != self._numChannels:
			raise nsp.Errors.BadArgumentError("Wrong number of sim data channels.")
		
		index = self._index(frame)
		if index >= self._numFrames:
			# Make sure each channel has an entry for the current frame
			extraFrames = (frame - self._numFrames + 1)
			if 1 == extraFrames:
				for channel in self._channels:
					channel.append( 0.0 )
			else:
				for channel in self._channels:
					channel.extend( [ 0.0 ] * extraFrames )
			self._numFrames = frame + 1
		
		# Add the sample to each channel
		for i in range(self._numChannels):
			self._channels[i][index] = data[i]
			
	def _index(self, frame):
		return frame - self._startFrame
