from gravitate.data_access import EventDao

from gravitate.scripts.event_builders import LaxEventBuilder, UcsbEventBuilder
from gravitate.scripts.utils import generateStartDatetime, generateTimestamps


def generateAirportEvents(timestampTupleList: list):
    eventList = list()

    for startTimestamp, endTimestamp in timestampTupleList:
        newEvent = LaxEventBuilder(startTimestamp, endTimestamp)
        eventList.append(newEvent)

    return eventList


def generateUcEvents(timestampTupleList: list):
    eventList = list()

    for startTimestamp, endTimestamp in timestampTupleList:
        newEvent = UcsbEventBuilder(startTimestamp, endTimestamp)
        eventList.append(newEvent)

    return eventList


def populateEvents(startString="2018-12-07T08:00:00.000", numDays=35, eventCategory="airport"):
    startDatetime = generateStartDatetime(startString)
    timestampTupleList = generateTimestamps(startDatetime, numDays)
    assert eventCategory == "airport" or eventCategory == "campus"
    eventList = generateAirportEvents(timestampTupleList) if eventCategory == "airport" else generateUcEvents(
        timestampTupleList)
    for event in eventList:
        eventRef = EventDao().create(event)
        print(eventRef)
