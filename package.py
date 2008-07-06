import os
import os.path
import shutil
import py_compile

_srcRoot = "C:/svn/msvImporter"
_pySrcRoot = "%s/python" % _srcRoot
_dstRoot = "C:/sandbox/msv"

_pyDstRoot = "%s/python" % _dstRoot
_pluginsDstRoot = "%s/plug-ins" % _dstRoot
_scriptsDstRoot = "%s/scripts" % _dstRoot
_iconsDstRoot = "%s/icons" % _dstRoot

_pluginFiles = [ "plug-ins/MsvTools.py" ]

_pyFiles = [
		"ns/py/Errors.py",
		"ns/py/RollbackImporter.py",
		"ns/py/Timer.py",
		"ns/maya/Progress.py",
		"ns/maya/live/MayaServer.py",
		"ns/maya/msv/Agent.py",
		"ns/maya/msv/AgentDescription.py",
		"ns/maya/msv/AMCReader.py",
		"ns/maya/msv/APFReader.py",
		"ns/maya/msv/CallsheetReader.py",
		"ns/maya/msv/CDLReader.py",
		"ns/maya/msv/MasDescription.py",
		"ns/maya/msv/MasReader.py",
		"ns/maya/msv/MasWriter.py",
		"ns/maya/msv/MayaAgent.py",
		"ns/maya/msv/MayaPlacement.py",
		"ns/maya/msv/MayaScene.py",
		"ns/maya/msv/MsvImporterCmd.py",
		"ns/maya/msv/MsvSimLoader.py",
		"ns/maya/msv/SceneDescription.py",
		"ns/maya/msv/Selection.py",
		"ns/maya/msv/Sim.py",
		"ns/maya/msv/SimReader.py",
		"ns/maya/msv/WReader.py",
		"ns/msv/MsvPlacement.py",
		"ns/msv/PullMaya.py",
		"ns/msv/PushMaya.py"
		]

_melFiles = [
		"scripts/msvCombiner.mel",
		"scripts/msvImporterWin.mel",
		"scripts/msvSceneWin.mel",
		"scripts/msvSceneUtils.mel",
		]

_extraFiles = [
		"INSTALL.txt",
		"LICENSE.txt",
		"CHANGES.txt",
		"MsvTools.txt",
		"MsvTranslator.py"
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
		
	copyPythonFiles( _pySrcRoot, _pyDstRoot, _pyFiles, flatten=False, compile=False )
	copyPythonFiles( _srcRoot, _pluginsDstRoot, _pluginFiles, flatten=True, compile=False )
	copyFiles( _srcRoot, _scriptsDstRoot, _melFiles, True )
	copyFiles( _srcRoot, _dstRoot, _extraFiles, True )
	copyFiles( _srcRoot, _iconsDstRoot, _iconFiles, True )

if __name__ == "__main__":
	main()