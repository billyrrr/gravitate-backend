# Author: Andrew Kim
from models.event import Event

def setEventAsActive(e = Event()):
	""" Definition
	    Sets the event object's boolean flag to True
	    
	    :param e:
	""" 
	e.eventStatus = True
	
def setEventAsPast(e = Event()):
	""" Definition
	    Sets the event object's boolean flag to False
	
	    :param e:
	"""
	e.eventStatus = False
