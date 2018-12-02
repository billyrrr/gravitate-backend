#Author: Andrew Kim
import datetime
from models.event import Event

event: Event
ts = datetime.datetime.now().timestamp()

class EventStatus:
	
	@staticmethod
	def eventStatus():
		""" Definition
		    Sets the event to a past event category one day after the start time
		"""
		#check if eventStatus is True before proceeding
		if event.isClosed = False:
			if ts >= event.endTimestamp:
				event.isClosed = True

