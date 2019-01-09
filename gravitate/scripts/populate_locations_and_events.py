from gravitate.scripts.location import populate_locations
from gravitate.scripts.event import populate_airport_events

# Populate database for uc/campus location and events
populate_locations.doWorkUc("UCSB")
populate_airport_events.populate_events(start_string="2018-12-20T08:00:00.000", num_days=15, event_category="campus")

# Populate database for airport location and events
populate_locations.doWork()
populate_airport_events.populate_events(start_string="2018-12-17T08:00:00.000", num_days=3)
