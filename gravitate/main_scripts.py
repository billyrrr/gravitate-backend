from gravitate.scripts import populate_locations
from gravitate.scripts import populate_airport_events

populate_locations.doWorkUc("UCSB")
populate_airport_events.populateEvents(startString="2018-12-06T08:00:00.000", numDays=35, eventCategory="campus")
# # Populate database for airport location and events
# populate_locations.doWork()
# populate_airport_events.populateEvents(startString="2018-12-06T08:00:00.000", numDays=35)
