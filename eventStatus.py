#Author: Andrew Kim

from models.event import Event

event: Event

class EventStatus:
	
	@staticmethod
	def eventStatus(timeAfterFlight):
		""" Definition
		    Sets the event to a past event category one day after the start time
		    :param timeAfterFlight:
		"""
		#check if eventStatus is True before proceeding
		if event.eventStatus = True:
			if event.startTimestamp >= event.startTimeStamp + timeAfterFlight:
				event.eventStatus = False
