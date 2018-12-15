#Author: Andrew Kim
import datetime
from models import Event

def eventStatus(event: Event):
	""" Definition
		Sets the event to a past event category one day after the start time 
	"""
	ts = datetime.datetime.now().timestamp()
	#check if eventStatus is True before proceeding
	if not event.isClosed and ts >= event.endTimestamp:
		return True
	else:
		return False

def closeEvent(event: Event):
	event.isClosed = True
