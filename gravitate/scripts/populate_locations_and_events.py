from gravitate.scripts.event import populate_airport_events
from gravitate.scripts.location import populate_locations

if __name__ == "__main__":
    #
    # Populate database for uc/campus location and events
    populate_locations.doWorkUc("UCSB")
    populate_airport_events.populate_events(start_string="2019-03-23T08:00:00.000", num_days=10, event_category="campus")
    #
    # # Populate database for airport location and events
    # populate_locations.doWork()
    # populate_airport_events.populate_events(start_string="2019-03-23T08:00:00.000", num_days=90)

