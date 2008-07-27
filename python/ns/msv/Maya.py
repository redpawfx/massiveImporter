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
import socket
import thread

import massive

import ns.bridge.data.MasSpec as MasSpec
import ns.bridge.io.MasWriter as MasWriter
import ns.bridge.io.MasReader as MasReader
import ns.py.Errors as Errors
import ns.msv.MsvPlacement as MsvPlacement

def Push(groups="sync"):
	
	# create Internet TCP socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	host = 'localhost' # server address
	port = 51234 # server port
	
	try:
		try:
			print >> sys.stderr, "CONNECTING TO SERVER"
			# connect to server
			s.connect((host, port))
			
			file = s.makefile("rw", 0)
		
			if type(groups) != list:
				if groups == "sync":
					file.write("PUSH sync\n")
					fromMaya = MasReader.read(file)
					groups = []
					for group in fromMaya.groups:
						groups.append(group.name)
				else:
					raise Errors.BadArgumentError("%s is not a supported 'groups' value." % groups)
			else:
				file.write("PUSH\n")
		
			MsvPlacement.dump(file, groups)
		except Exception, e:
			print >> sys.stderr, e
	finally:
		s.close() # close socket
		print >> sys.stderr, "CONNECTION CLOSED"

def Pull():
	# create Internet TCP socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	host = 'localhost' # server address
	port = 51234 # server port
	
	try:
		print >> sys.stderr, "CONNECTING TO SERVER"
		# connect to server
		s.connect((host, port))
		
		file = s.makefile("rw", 0)
		
		file.write("PULL\n")
		
		#for line in file.readlines():
		#	print >> sys.stderr, line.strip()
	
		mas = MasReader.read(file)
		MsvPlacement.build(mas)
	finally:
		s.close() # close socket
		print >> sys.stderr, "CONNECTION CLOSED"
