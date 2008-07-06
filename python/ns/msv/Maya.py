import sys
import socket
import thread

import massive

import ns.maya.msv.MasDescription as MasDescription
import ns.maya.msv.MasWriter as MasWriter
import ns.maya.msv.MasReader as MasReader
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
