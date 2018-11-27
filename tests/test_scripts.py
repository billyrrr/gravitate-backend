import unittest

from scripts.populate_locations import buildLaxTerminal

class TestBuildLaxTerminal(unittest.TestCase):
    
    def testBuildTerminal1(self):
        buildLaxTerminal("1")