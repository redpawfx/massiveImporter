import sys
import socket
import threading

import maya.utils

import ns.maya.msv.MayaPlacement as MayaPlacement


class MayaServer( threading.Thread ):
	
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		# set up Internet TCP socket
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		# server port number
		port = 51234 
		# bind lstn socket to this port
		serverSocket.bind(('localhost', port))
		# start listening for contacts from clients (at most 1 at a time)
		serverSocket.listen(1)
		
		while True:
			(clientSocket, address) = serverSocket.accept()
			Connection( clientSocket, address ).start()

class Connection( threading.Thread ):
	
	def __init__(self, socket, address):
		threading.Thread.__init__(self)
		self._socket = socket
		self._file = socket.makefile("rw", 0)
		self._address = address
		
	def run(self):
		request = self._file.readline().strip()
		if request == "PULL":
			maya.utils.executeInMainThreadWithResult( MayaPlacement.dump, self._file ) 
		elif request == "PUSH":
			maya.utils.executeInMainThreadWithResult( MayaPlacement.build, self._file ) 
		else:
			print >> sys.stderr, "%s: INVALID" % request
		
		# Client's 'readlines' won't pick anythin up until we close the file
		# and socket
		self._file.close()
		self._socket.close()
		