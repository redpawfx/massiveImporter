import sys
import socket
import threading

import maya.utils
import maya.cmds as mc

import ns.maya.msv.MayaPlacement as MayaPlacement
import ns.py.Errors as Errors

def threadPrint(msg):
	print msg

class MayaServer( threading.Thread ):
	
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		self._running = True
		# set up Internet TCP socket
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# allows the server to be killed. Setting the timeout too
		# low, though, (like 0) consumes all available cpu cycles
		self._socket.settimeout(1)
		
		# server port number
		port = 51234 
		# bind lstn socket to this port
		self._socket.bind(('localhost', port))
		# start listening for contacts from clients (at most 1 at a time)
		self._socket.listen(1)
		
		while self._running:
			try:
				# the socket is non-blocking so every second that
				# goes by without a connectionit will raise an
				# exception. I really should only catch the
				# exact exception type raised in this case.
				(clientSocket, address) = self._socket.accept()
				Connection( clientSocket, address ).start()
			except:
				pass
			
		maya.utils.executeInMainThreadWithResult( threadPrint, "Shutting down server..." ) 
			
	def stop(self):
		self._running = False

class Connection( threading.Thread ):
	
	def __init__(self, socket, address):
		threading.Thread.__init__(self)
		self._socket = socket
		self._file = socket.makefile("rw", 0)
		self._address = address
		
	def run(self):
		try:
			request = self._file.readline().split()
			if request[0] == "PULL":
				maya.utils.executeInMainThreadWithResult( MayaPlacement.dump, self._file ) 
			elif request[0] == "PUSH":
				if len(request) == 1:
					maya.utils.executeInMainThreadWithResult( MayaPlacement.build, self._file ) 
				elif request[1] == "sync":
					maya.utils.executeInMainThreadWithResult( threadPrint, "PUSH sync" ) 
				else:
					raise Errors.BadArgumentError("%s: INVALID" % request)
			else:
				raise Errors.BadArgumentError("%s: INVALID" % request)
		finally:
			# Client's 'readlines' won't pick anythin up until we close the file
			# and socket
			self._file.close()
			self._socket.close()
		