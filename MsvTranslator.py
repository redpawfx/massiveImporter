import sys
import os
import os.path

try:
	import maya.standalone
	import maya.cmds as mc
	import maya.mel
except:
	print >> sys.stderr, "Please use the 'mayapy' executable included in your installation of Maya to run MsvTranslator.py"
	exit(1)

try:
	import ns.py.Timer as Timer
	import ns.maya.msv.MsvImporterCmd as MsvImporterCmd
	import ns.bridge.io.MasReader as MasReader
except:
	print >> sys.stderr, "Please set your PYTHONPATH to include the MsvTools 'python' directory"
	exit(1)

kOutputDirFlag = "-out"
kOutputDirFlagLong = "-outputDir"
kOutputTypeFlag = "-typ"
kOutputTypeFlagLong = "-type"
kGroupSizeFlag = "-gs"
kGroupSizeFlagLong = "-groupSize"

def parseArgs():
	flags = ""
	args = { 'groupSize' : -1,
			 'outputType' : 'mayaAscii' }
	argc = len(sys.argv)
	i = 1
	while i < argc:
		arg = sys.argv[i]
		if arg == kOutputDirFlagLong or arg == kOutputDirFlag:
			i += 1
			args['outputDir'] = sys.argv[i]
		elif arg == kGroupSizeFlagLong or arg == kGroupSizeFlag:
			i += 1
			args['groupSize'] = int(sys.argv[i])
		elif arg == kOutputTypeFlag or arg == kOutputTypeFlagLong:
			i += 1
			args['outputType'] = sys.argv[i]
		elif arg[0] == '-':
			flags += " %s" % arg
		else:
			try:
				# This will throw an exception if arg is not the
				# string representation of an int or a float
				#
				float(arg)
				flags += ' %s' % arg
			except:
				flags += ' \\"%s\\"' % arg

		# The -masFile is passed through to the command, but we
		# also need it to query the number of agents and correctly
		# divide up the load
		#		
		if (arg == MsvImporterCmd.kMasFileFlagLong or
		    arg == MsvImporterCmd.kMasFileFlag):
			args['masFile'] = sys.argv[i+1]
			
		i += 1
		
	return (args, flags)

def mayaFileSuffix(outputType):
	if outputType == "mayaAscii":
		return "ma"
	elif outputType == "mayaBinary":
		return "mb"
	else:
		raise Exception("%s is not a valid Maya file type." % outputType)

def main():
	Timer.push("MsvTranslator")
	
	(args, flags) = parseArgs()
	
	if not args['masFile'] or not args['outputDir']:
		raise Exception("Both the -masFile and -outputDir flags must be specified.")
	
	mas = MasReader.read(args['masFile'])
	basename = os.path.splitext(os.path.basename(args['masFile']))[0]

	fileSuffix = mayaFileSuffix( args['outputType'] )
	groupSize = args['groupSize']
	if groupSize < 1:
		groupSize = mas.numAgents
	
	finalLog = "%s/%s.log" % (args['outputDir'], basename)
	tempLog = "%s/%s.temp.log" % (args['outputDir'], basename)
	
	for group in range(1, mas.numAgents+1, groupSize ):
		currentFile = ""
		rangeStr = ""
		if groupSize < mas.numAgents:
			currentFile = "%s/%s_%d.%s" % (args['outputDir'], basename, group, fileSuffix)
			if groupSize == 1:
				rangeStr = ' -range \\"%s\\"' % str(group)
			else:
				rangeStr = ' -range \\"%d-%d\\"' % (group, group + groupSize - 1)
		else:
			currentFile = "%s/%s.%s" % (args['outputDir'], basename, fileSuffix)

		# Ideally we could do this as a standalone script using
		# maya.standalone. However, for some reason, when nsImportMsv
		# is run as part of a standalone script it doesn't work right.
		# For example, extra anim curves get created for ry and rz
		# when only rx is keyed, and the keyed values are not correctly
		# saved out to disk. Running it as part of maya batch, however,
		# seems to work fine. This may be because nsImportMsv is implemented
		# using the python interface to MEL as opposed to the API and 
		# maya.standalone is, perhaps, intended for use with the python
		# API bindings (although this is pure speculation).
		#
		
		mel = 'cmdFileOutput -o \\"%s\\";' % tempLog
		mel += ' loadPlugin \\"MsvTools.py\\";'
		mel += ' msvImporter%s%s;' % (rangeStr, flags)
		mel += ' file -rename \\"%s\\";' % currentFile
		mel += ' file -f -uc 0 -type \\"%s\\" -save;' % args['outputType']
		mel += ' cmdFileOutput -closeAll;'
	
		batchCmd = 'maya -batch -command "%s"' % mel
		print >> sys.stderr, batchCmd
		os.system(batchCmd)
		
		tempLogFile = open( tempLog, "r" )
		finalLogFile = open( finalLog, "a" )
		finalLogFile.writelines( tempLogFile.readlines() )
		finalLogFile.close()
		tempLogFile.close()
		
	if groupSize < mas.numAgents:
		mel = 'cmdFileOutput -o \\"%s\\";' % tempLog
		mel += ' msvCombiner( \\"%s\\", \\"%s\\", \\"%s\\", %d, %d );' % (args['outputDir'], basename, args['outputType'], groupSize, mas.numAgents)
		mel += ' cmdFileOutput -closeAll;'
		batchCmd = 'maya -batch -command "%s"' % mel
		print >> sys.stderr, batchCmd
		os.system(batchCmd)
		
		tempLogFile = open( tempLog, "r" )
		finalLogFile = open( finalLog, "a" )
		finalLogFile.writelines( tempLogFile.readlines() )
		finalLogFile.close()
		tempLogFile.close()
		
	os.remove( tempLog )
		
	Timer.pop()
		
	print >> sys.stderr, ""
	print >> sys.stderr, "######################################################################"
	print >> sys.stderr, "### Done in %f seconds" % Timer.elapsed("MsvTranslator")
	print >> sys.stderr, "### %s" % args['masFile']
	print >> sys.stderr, "### converted to"
	print >> sys.stderr, "### %s/%s.%s" % (args['outputDir'], basename, fileSuffix)
	print >> sys.stderr, "###"
	print >> sys.stderr, "### See %s for a log of results." % finalLog
	print >> sys.stderr, "######################################################################"
	print >> sys.stderr, ""
	
	exit(0)
    
if __name__ == "__main__":
    main()