from gravitate import scripts


def generate_test_data():
    scripts.populate_locations.doWork()
    scripts.populate_airport_events.populate_events(start_string="2018-12-19T08:00:00.000", num_days=15)


if __name__ == "__main__":
    scripts.delete_all_events()
    scripts.delete_all_locations()
    generate_test_data()
