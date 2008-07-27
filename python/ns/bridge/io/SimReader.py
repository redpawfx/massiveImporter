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

import ns.bridge.io.AMCReader as AMCReader
import ns.bridge.io.APFReader as APFReader

def _readAPFSim( simFiles, simData ):
	# Sort the files first to guarantee that samples are added to the sim
	# in sequential order. Otherwise it becomes awkward to manage the channel
	# data if the sim doesn't always start at frame 1
	#
	apfFiles = []
	for simFile in simFiles:
		apfFiles.append( APFReader.APFReader( simFile ) )
	
	apfFiles.sort( APFReader.APFReader.cmp )

	for apfFile in apfFiles:
		apfFile.read( simData )

def _readAMCSim( simFiles, simData ):
	for simFile in simFiles:
		AMCReader.read( simFile, simData )

def read(simDir, simType, simData):
	'''Load sim files from a sim directory'''
	
	try:
		simFiles = [ "%s/%s" % (simDir, file) for file in os.listdir(simDir) if os.path.splitext(file)[1] == simType ]
		
		if not simFiles:
			print >> sys.stderr, "Warning: no sim files of type %s found." % simType
			return
		
		if ".amc" == simType:
			return _readAMCSim( simFiles, simData )
		elif ".apf" == simType:
			return _readAPFSim( simFiles, simData )
		else:
			raise "Unknown sim type: %s" % simType
	 		
 	except:
 		print >> sys.stderr, "Error reading simulation: %s" % simDir	
 		raise

        
