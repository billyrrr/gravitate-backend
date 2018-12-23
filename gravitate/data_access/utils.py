import random
import string

# Generate a random string
# with 32 characters.
# https://www.geeksforgeeks.org/generating-random-ids-python/
def randomId():
    randomIdStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    return randomIdStr