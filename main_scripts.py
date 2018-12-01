from scripts import populate_locations
from scripts import populate_airport_events

populate_locations.doWork()

populate_airport_events.populateEvents(startString = "2018-12-01T08:00:00.000", numDays = 35)