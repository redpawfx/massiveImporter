import os
import os.path
import shutil
import py_compile

_srcRoot = "C:/svn/msvimporter"
_pySrcRoot = "%s/python" % _srcRoot
_dstRoot = "C:/sandbox/msv"

_pyDstRoot = "%s/python" % _dstRoot
_pluginsDstRoot = "%s/plug-ins" % _dstRoot
_scriptsDstRoot = "%s/scripts" % _dstRoot
_iconsDstRoot = "%s/icons" % _dstRoot
_testsDstRoot = "%s/tests" % _dstRoot

_pluginFiles = [ "plug-ins/MsvTools.py" ]

_pyFiles = [
		"ns/py/Errors.py",
		"ns/py/RollbackImporter.py",
		"ns/py/Timer.py",
		"ns/maya/Progress.py",
		"ns/maya/live/MayaServer.py",
		"ns/bridge/data/Scene.py",
		"ns/bridge/data/Sim.py",
		"ns/bridge/data/Agent.py",
		"ns/bridge/data/AgentSpec.py",
		"ns/bridge/data/Brain.py",
		"ns/bridge/io/AMCReader.py",
		"ns/bridge/io/APFReader.py",
		"ns/bridge/io/CallsheetReader.py",
		"ns/bridge/io/CDLReader.py",
		"ns/bridge/io/CDLWriter.py",
		"ns/bridge/data/MasSpec.py",
		"ns/bridge/io/MasReader.py",
		"ns/bridge/io/MasWriter.py",
		"ns/maya/msv/MayaAgent.py",
		"ns/maya/msv/MayaSkin.py",
		"ns/maya/msv/MayaSceneAgent.py",
		"ns/maya/msv/MayaSimAgent.py",
		"ns/maya/msv/MayaPlacement.py",
		"ns/maya/msv/MayaScene.py",
		"ns/maya/msv/MayaSim.py",
		"ns/maya/msv/MayaUtil.py",
		"ns/maya/msv/MsvSceneExportCmd.py",
		"ns/maya/msv/MsvSceneImportCmd.py",
		"ns/maya/msv/MsvSimImportCmd.py",
		"ns/maya/msv/MsvSimLoader.py",
		"ns/bridge/data/Selection.py",
		"ns/bridge/data/SimData.py",
		"ns/bridge/io/SimReader.py",
		"ns/bridge/io/WReader.py",
		"ns/msv/MsvPlacement.py",
		"ns/msv/Maya.py"
		]

_melFiles = [
		"scripts/msvCombiner.mel",
		"scripts/msvSimImportWin.mel",
		"scripts/msvSceneWin.mel",
		"scripts/msvSceneUtils.mel",
		]

_extraFiles = [
		"INSTALL.txt",
		"LICENSE.txt",
		"CHANGES.txt",
		"MsvTools.txt",
		"MsvTranslator.py",
		"MsvEvolve.py"
		]

_testFiles = [
		"tests/TestIO.py",
		"tests/TestGenotype.py"
		]

_iconFiles = [
		]
		
def copyPythonFiles( srcRoot, dstRoot, files, flatten, compile ):
	for file in files:
		src = "%s/%s" % (srcRoot, file)
		dst = ""
		if flatten:
			(srcPath, srcFile) = os.path.split( file )
			dst = "%s/%s" % (dstRoot, srcFile)
		else:
			dst = "%s/%s" % (dstRoot, file)
			chunks = file.split("/")
			dstPath = dstRoot
			srcPath = srcRoot
			for chunk in chunks:
				srcPath = "%s/%s" % (srcPath, chunk)
				if not os.path.isdir(srcPath):
					break
				dstPath = "%s/%s" % (dstPath, chunk)
				if not os.path.isdir(dstPath):
					os.mkdir(dstPath)
					srcInit = "%s/__init__.py" % srcPath
					dstInit = "%s/__init__.py" % dstPath
					if not os.path.exists( srcInit ):
						raise IOError( "%s does not exist" % srcInit )
					shutil.copyfile( srcInit, dstInit )
					if compile:
						py_compile.compile( dstInit )
						os.remove( dstInit )
		shutil.copyfile( src, dst )
		if compile:
			py_compile.compile( dst )
			os.remove( dst )
			
def copyFiles( srcRoot, dstRoot, files, flatten ):
	for file in files:
		src = "%s/%s" % (srcRoot, file)
		dst = ""
		if flatten:
			(srcPath, srcFile) = os.path.split( file )
			dst = "%s/%s" % (dstRoot, srcFile)
		else:
			dst = "%s/%s" % (dstRoot, file)
			chunks = file.split("/")
			dstPath = dstRoot
			srcPath = srcRoot
			for chunk in chunks:
				srcPath = "%s/%s" % (srcPath, chunk)
				if not os.path.isdir(srcPath):
					break
				dstPath = "%s/%s" % (dstPath, chunk)
				if not os.path.isdir(dstPath):
					os.mkdir(dstPath)
		shutil.copyfile( src, dst )
		
def main():
	if not os.path.isdir(_dstRoot):
		os.mkdir(_dstRoot)	
	if not os.path.isdir(_pyDstRoot):
		os.mkdir(_pyDstRoot)
	if not os.path.isdir(_pluginsDstRoot):
		os.mkdir(_pluginsDstRoot)
	if not os.path.isdir(_scriptsDstRoot):
		os.mkdir(_scriptsDstRoot)
	if not os.path.isdir(_iconsDstRoot):
		os.mkdir(_iconsDstRoot)
	if not os.path.isdir(_testsDstRoot):
		os.mkdir(_testsDstRoot)
				
	copyPythonFiles( _pySrcRoot, _pyDstRoot, _pyFiles, flatten=False, compile=False )
	copyPythonFiles( _srcRoot, _pluginsDstRoot, _pluginFiles, flatten=True, compile=False )
	copyFiles( _srcRoot, _scriptsDstRoot, _melFiles, True )
	copyFiles( _srcRoot, _dstRoot, _extraFiles, True )
	copyFiles( _srcRoot, _testsDstRoot, _testFiles, True )
	copyFiles( _srcRoot, _iconsDstRoot, _iconFiles, True )

if __name__ == "__main__":
	main()