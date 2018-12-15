"""
Author: Zixuan Rao
Reference: https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure/24266885#24266885

"""


import sys
import unittest

sys.path.append('../gravitate-backend')

loader = unittest.TestLoader()
testSuite = loader.discover('test')
testRunner = unittest.TextTestRunner(verbosity=2)
testRunner.run(testSuite)
