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

import sys
import os
import unittest

import ns.tests.TestIO as TestIO
import ns.tests.TestGenotype as TestGenotype
import ns.tests.TestMutateOutput as TestMutateOutput
import ns.tests.TestMutateDefuzz as TestMutateDefuzz
import ns.tests.TestMutateOr as TestMutateOr
import ns.tests.TestMutateAnd as TestMutateAnd
import ns.tests.TestMutateFuzz as TestMutateFuzz
import ns.tests.TestMutateNoise as TestMutateNoise
import ns.tests.TestMutateTimer as TestMutateTimer
import ns.tests.TestMutateInput as TestMutateInput

if __name__ == '__main__':
	try:
		suites = [ #TestIO.suite,
				   #TestGenotype.suite,
				   #TestMutateOutput.suite,
				   #TestMutateDefuzz.suite,
				   #TestMutateOr.suite,
				   #TestMutateAnd.suite,
				   #TestMutateFuzz.suite,
				   #TestMutateNoise.suite,
				   #TestMutateTimer.suite,
				   TestMutateInput.suite ]
		allTests = unittest.TestSuite(suites)

		unittest.TextTestRunner(verbosity=2).run(allTests)

	finally:
		sys.exit()