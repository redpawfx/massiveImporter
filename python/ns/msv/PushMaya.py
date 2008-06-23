import sys
import socket
import thread

import ns.maya.msv.MasDescription as MasDescription
import ns.maya.msv.MasWriter as MasWriter

def PushMaya():
	# create Internet TCP socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	print >> sys.stderr, "CONNECTING TO SERVER"
	host = 'localhost' # server address
	port = 51234 # server port
	
	# connect to server
	s.connect((host, port))
	
	file = s.makefile("rw", 0)
	
	file.write("PUSH\n")

	mas = MasDescription.MasDescription()
	mas.groups.append(MasDescription.Group(0, "zero"))
	mas.groups.append(MasDescription.Group(1, "one"))
	mas.locators.append(MasDescription.Locator(0, [1, 2, 3]))
	mas.locators.append(MasDescription.Locator(0, [2, 3, 4]))
	mas.locators.append(MasDescription.Locator(1, [5, 6, 7]))
	
	MasWriter.write(file, mas)
	
	#while(1):
	#	# get letter
	#	k = raw_input('enter a letter:')
	#	s.send(k) # send k to server
	#	# if stop signal, then leave loop
	#	if k == '': break
	#	v = s.recv(1024) # receive v from server (up to 1024 bytes)
	#	print v
	#
	#print >> sys.stderr, "CLOSING CLIENT"
	s.close() # close socket
	print >> sys.stderr, "CONNECTION CLOSED"
