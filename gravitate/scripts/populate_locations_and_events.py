from gravitate.scripts.location import populate_locations
from gravitate.scripts.event import populate_airport_events

# Populate database for uc/campus location and events
populate_locations.doWorkUc("UCSB")
populate_airport_events.populateEvents(startString="2018-12-20T08:00:00.000", numDays=15, eventCategory="campus")

# Populate database for airport location and events
populate_locations.doWork()
populate_airport_events.populateEvents(startString="2018-12-20T08:00:00.000", numDays=15)
