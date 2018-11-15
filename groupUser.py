# Author: Tyler Song

import datetime

class GroupUsers:

    @staticmethod
    def groupUsers(arr, groupTime):     #array of pairs where the first elem is departure time
                                        #second elem is unique user id.

        # sorted array by time in increasing order
        sortedArr = sorted(
            arr, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d-%H:%M'))

        print(sortedArr)

        paired = []  # array of paired users
        notpaired = []  # array of unpaired users

        i = 0  # generic loop counter

        while i < len(sortedArr):  # iterate through sortedArr
            if i == len(sortedArr) - 1:  # case where there is only 1 user left
                notpaired.insert(len(notpaired), [
                                sortedArr[i][0], sortedArr[i][1]])
                i += 1
            else:
                datetime_obj = datetime.datetime.strptime(
                    sortedArr[i][0], '%Y-%m-%d-%H:%M')  # 2 datetime objs from the array
                datetime_obj2 = datetime.datetime.strptime(
                    sortedArr[i+1][0], '%Y-%m-%d-%H:%M')

                # get maximum allowable time difference
                maxRange = datetime_obj + datetime.timedelta(minutes=groupTime)

                print('Comparing request 1:', datetime_obj,
                    'and request 2:', datetime_obj2)

                if maxRange >= datetime_obj2:  # found an eligible group
                    print('In range of', groupTime)
                    paired.insert(
                        len(paired), [sortedArr[i][1], sortedArr[i+1][1]])
                    i += 1
                else:  # did not find an eligible group
                    print('Not in range of', groupTime)
                    notpaired.insert(len(notpaired), [
                                    sortedArr[i][0], sortedArr[i][1]])

                i += 1

        print('paired list:', paired)
        print('unpaired list:', notpaired)

        return


groupTime = 30  # maximum time difference of 30 minutes

# array of departure time followed by unique user ID
arr = [['2018-2-25-9:00', '1'],  ['2018-2-24-9:40', '2'],
           ['2018-2-24-9:50', '3'], ['2018-2-25-9:40', '4'], ['2018-2-26-9:50', '5']]

GroupUsers.groupUsers(arr, groupTime)
