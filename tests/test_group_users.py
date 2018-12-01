from controllers.group_user import pair
import unittest


class TestGroupUsers(unittest.TestCase):

    def testPairAlgorithm(self):
        arr = [[12000000, 12005000, 'A'], [12000000, 12005000, 'B'],
               [12000000, 12005000, 'C'], [12005000, 12006000, 'D'],
               [12007000, 12009000, 'E'], [12009001, 12009900, 'F'],
               [11000000, 11009000, 'G']]

        paired = []
        unpaired = []

        pair(arr=arr, paired=paired, unpaired=unpaired)

        print('paired list:', paired)
        print('unpaired list:', unpaired)
