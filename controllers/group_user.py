"""

	Author: Tyler, Zixuan Rao

"""

def pair(arr = None, paired: list = None, unpaired: list = None):
	"""
	Description: 

		Author: Tyler

		:param arr:  an array of ride requests
			[the first is earliest allowable time, second is latest time, third is firestore reference]
		:param paired: 
		:param unpaired: 
	"""
	sortedArr = sorted(arr, key=lambda x: x[0])

	i=0
	while i < len(sortedArr):

		if i == len(sortedArr) - 1:
			unpaired.insert(len(unpaired), [sortedArr[i][2]])
			i+=1
		else:
			if(sortedArr[i][1] >= sortedArr[i+1][0]):

				paired.insert(len(paired), [sortedArr[i][2], sortedArr[i+1][2]])
				i+=1
			else:

				unpaired.insert(len(unpaired), [sortedArr[i][2]])
			i+=1