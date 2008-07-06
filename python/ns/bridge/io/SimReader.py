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

import ns.py.Timer as Timer
import ns.maya.Progress as Progress

import ns.bridge.io.AMCReader as AMCReader
import ns.bridge.io.APFReader as APFReader

def _readAPFSim( simFiles, sim, progressRange ):
	# Sort the files first to guarantee that samples are added to the sim
	# in sequential order. Otherwise it becomes awkward to manage the channel
	# data if the sim doesn't always start at frame 1
	#
	apfFiles = []
	for simFile in simFiles:
		apfFiles.append( APFReader.APFReader( simFile ) )
	
	apfFiles.sort( APFReader.APFReader.cmp )

	progressIncrement = int(progressRange / len(apfFiles))	
	for apfFile in apfFiles:
		Timer.push("Read APF")
		Progress.setProgressStatus(os.path.basename(apfFile.fullName))
		apfFile.read( sim )
		Progress.advanceProgress( progressIncrement )
		Timer.pop()

def _readAMCSim( simFiles, sim, progressRange ):
	progressIncrement = int(progressRange / len(simFiles))	
	for simFile in simFiles:
		Progress.setProgressStatus(os.path.basename(simFile))
		Timer.push("Read AMC")
		amcFile = AMCReader.AMCReader( simFile )
		amcFile.read( sim )
		Timer.pop()
		Progress.advanceProgress( progressIncrement )

def read(dirPath, simType, sim, progressRange=0):
	'''Load sim files from a sim directory'''
	
	try:
		simFiles = [ "%s%s" % (dirPath, file) for file in os.listdir(dirPath) if os.path.splitext(file)[1] == simType ]
		
		if not simFiles:
			print >> sys.stderr, "Warning: no sim files of type %s found." % simType
			return
		
		if ".amc" == simType:
			return _readAMCSim( simFiles, sim, progressRange )
		elif ".apf" == simType:
			return _readAPFSim( simFiles, sim, progressRange )
		else:
			raise "Unknown sim type: %s" % simType
	 		
 	except:
 		print >> sys.stderr, "Error reading simulation: %s" % dirPath	
 		raise

        
