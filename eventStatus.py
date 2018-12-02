#Author: Andrew Kim
import datetime
from models.event import Event

event: Event
ts = datetime.datetime.now().timestamp()

class EventStatus:
	
	@staticmethod
	def eventStatus(timeAfterEventStart):
		""" Definition
		    Sets the event to a past event category one day after the start time
		    :param timeAfterFlight:
		"""
		#check if eventStatus is True before proceeding
		if event.isClosed == False:
			if ts >= event.startTimestamp + timeAfterEventStart:
				event.isClosed = True

