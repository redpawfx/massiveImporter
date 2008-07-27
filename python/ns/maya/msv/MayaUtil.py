# The MIT License
#	
# Copyright (c) 2008 James Piechota
#	
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from maya.OpenMaya import *
import maya.cmds as mc
import maya.mel as mel

def getDescendentShapes( name ):
	descendents = mc.listRelatives( name, allDescendents=True, fullPath=True )
	shapes = []
	if descendents:
		shapes = [ shape for shape in descendents if mc.objectType( shape, isAType="shape" ) ]	
	return shapes

def dagPathFromName(name):
	'''Return an instance of MDagPath() representing name.'''
	selList = MSelectionList()
	MGlobal.getSelectionListByName( name, selList )
	if selList.isEmpty():
		raise npy.Errors.BadArgumentError("%s not found" % name)
	dagPath = MDagPath()
	selList.getDagPath( 0, dagPath )
	return dagPath

def setMultiAttr( multiAttr, values, childAttr="" ):
	# Python allows a maximum of 255 arguments to a function/method call
	# so the maximum number of values we can process in a single setAttr
	# is 254 (255 minus 1 for the attribute name)
	chunkSize = min( 254, len(values) )
	if childAttr:
		childAttr = ".%s" % childAttr
	for chunk in range( 0, len(values), chunkSize ):
		# The last chunk may be smaller than chunkSize
		#
		curChunkSize = min( chunkSize, len(values) - chunk )
		
		stringValues = [ str(value) for value in values[chunk:chunk+curChunkSize] ]
		valString = ", ".join(stringValues)
		attr = "%s[%d:%d]%s" % (multiAttr, chunk, (chunk+curChunkSize-1), childAttr)
		eval('mc.setAttr( "%s", %s )' % (attr, valString))
		
		
def setMatrixAttr( matrixAttr, matrix ):
	'''Set a matrix attribute. This is always tricky because usually the matrix
	   data is stored in some sort of array structure, but Maya requires it to
	   be set as a comma-delimted list of values. Further complicated by the
	   fact that I haven't been able to get this to work using mc.setAttr(), so
	   have to fall back on calling the MEL setAttr command'''
	stringMatrix = [ str(value) for value in matrix ]
	arg = " ".join(stringMatrix)
	mel.eval('setAttr "%s" -type "matrix" %s' % (matrixAttr, arg))
	
def setDouble3Attr( double3Aattr, double3 ):
	'''Set a double3 attribute.'''
	stringDouble3 = [ str(value) for value in double3 ]
	arg = " ".join(stringDouble3)
	mel.eval('setAttr "%s" -type "double3" %s' % (double3Aattr, arg))

def hsvToRgb( hsv ):
	return mel.eval( 'hsv_to_rgb <<%f, %f, %f>>' % (hsv[0], hsv[1], hsv[2]) )

def rgbToHsv( rgb ):
	return mel.eval( 'rgb_to_hsv <<%f, %f, %f>>' % (rgb[0], rgb[1], rgb[2]) )

