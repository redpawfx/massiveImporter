import sys
import os
import os.path

import ns.py as npy
import ns.py.Errors
import ns.py.Timer as Timer

import ns.maya.msv as nmsv
import ns.maya.msv.MasReader as MasReader

masFile = "Y:/msvImporterData/mas/rtr/casual500.mas"
simDir = "Y:/msvImporterData/mas/Sim.cas500/"
callsheet = "Y:/msvImporterData/mas/rtr/casual500.call"
cacheDir = "Y:/msvImporterData/data/casual500"
loadGeometry = 1
loadSegments = 0
loadMaterials = 1
materialType = "lambert"
skinType = "smooth"
instanceSegments = 0
cacheGeometry = 1
deleteSkeleton = 1
simType = "apf"

outputDir = "Y:/msvImporterData/data/casual500"
outputType = "mayaAscii"
outputSuffix = ".ma"
groupSize = 200
basename = os.path.basename(masFile)
basename = os.path.splitext(basename)[0]

Timer.start("NimbleMsvShell")

mas = MasReader.read(masFile)

command = ""
for group in range(1, mas.numAgents+1, groupSize ):
	currentFile = "%s/%s_%d%s" % (outputDir, basename, group, outputSuffix)
	
	mel = 'loadPlugin \\"NimbleMsv.py\\";'
	mel += ' nsImportMsv'
	mel += ' -range \\"%d-%d\\"' % (group, group + groupSize -1)
	mel += ' -loadGeometry %d' % loadGeometry
	mel += ' -loadSegments %d' % loadSegments
	mel += ' -loadMaterials %d' % loadMaterials
	mel += ' -materialType \\"%s\\"' % materialType
	mel += ' -skinType "%s"' % skinType
	mel += ' -instanceSegments %d' % instanceSegments
	mel += ' -cacheGeometry %d' % cacheGeometry
	mel += ' -deleteSkeleton %d' % deleteSkeleton
	mel += ' -cacheDir \\"%s\\"' % cacheDir
	mel += ' -simType \\"%s\\"' % simType
	mel += ' -simDir \\"%s\\"' % simDir
	mel += ' -masFile \\"%s\\"' % masFile
	mel += ' -callsheet \\"%s\\"' % callsheet
	mel += ';'
	mel += 'file -rename \\"%s\\"; file -f -uc 0 -type \\"%s\\" -save;' % (currentFile, outputType)
	
	batchCmd = 'maya -batch -command "%s"' % mel
	print >> sys.stderr, batchCmd
	os.system(batchCmd)

combiner = 'nsImportMsvCombiner( \\"%s\\", \\"%s\\", \\"%s\\", %d, %d )' % (outputDir, basename, outputType, groupSize, mas.numAgents)
batchCmd = 'maya -batch -command "%s"' % combiner
print >> sys.stderr, batchCmd
os.system(batchCmd)


Timer.stop("NimbleMsvShell")

print >> sys.stderr, ""
print >> sys.stderr, "######################################################################"
print >> sys.stderr, "### Done in %f seconds" % Timer.elapsed("NimbleMsvShell")
print >> sys.stderr, "### %s" % masFile
print >> sys.stderr, "### converted to"
print >> sys.stderr, "### %s/%s%s" % (outputDir, basename, outputSuffix)
print >> sys.stderr, "######################################################################"
print >> sys.stderr, ""
