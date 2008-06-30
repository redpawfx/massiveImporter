import sys
import socket
import thread

import ns.maya.msv.MasReader as MasReader
import ns.msv.MsvPlacement as MsvPlacement

def PullMaya():
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
