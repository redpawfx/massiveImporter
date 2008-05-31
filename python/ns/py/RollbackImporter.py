#
# RollbackImporter from:
# http://pyunit.sourceforge.net/notes/reloading.html
#
# Updates:
# o Added ignore pattern
#
import sys
import __builtin__
import re

class RollbackImporter:
	def __init__(self, ignore):
		"Creates an instance and installs as the global importer"
		self.previousModules = sys.modules.copy()
		self.realImport = __builtin__.__import__
		__builtin__.__import__ = self._import
		self.newModules = {}
		self.ignore = ignore
		
	def _import(self, name, globals=None, locals=None, fromlist=[]):
		print >> sys.stderr, "_import %s" % name
		result = apply(self.realImport, (name, globals, locals, fromlist))
		self.newModules[name] = 1
		return result
		
	def uninstall(self):
		print >> sys.stderr, "uninstall"
		for modname in self.newModules.keys():
			print >> sys.stderr, "modname: %s" % modname
			# Don't uninstall modules that were imported prior to the 
			# RollbackImporter being initialized
			#
			if not self.previousModules.has_key(modname):
				# Don't uninstall modules that match the ignore patter
				#
				if not self.ignore or not re.search( self.ignore, modname ):
					# Force reload when modname next imported
					try:
						del(sys.modules[modname])
					except:
						print >> sys.stderr, "Error unininstalling %s" % modname
		__builtin__.__import__ = self.realImport