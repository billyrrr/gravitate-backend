"""

googlemaps python documentation: https://googlemaps.github.io/google-maps-services-python/docs/
"""

import googlemaps
import datetime

"""
Initialize google maps with key from project "gravitate-testing"
"""
gmaps = googlemaps.Client(key="AIzaSyARsDkedg2Q8dQdO4qGzgU9M9_jLFEjM5s")


# Test case
# Ref: https://github.com/googlemaps/google-maps-services-python
# Request directions via public transit
# now = datetime.datetime.now()
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)
# print(directions_result)


def get_distance_and_duration(origin, destination, mode="driving"):
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode=mode)
    # result = {'destination_addresses': ['Parramatta NSW 2150, Australia'],
    #           'origin_addresses': ['483 George St, Sydney NSW 2000, Australia'], 'rows': [{'elements': [
    #         {'distance': {'text': '25.1 km', 'value': 25093}, 'duration': {'text': '34 mins', 'value': 2026},
    #          'status': 'OK'}]}], 'status': 'OK'}
    row = result["rows"][0]
    elem = row["elements"][0]
    return elem


def get_coordinates(address=None):
    assert address is not None
    geocode_result = gmaps.geocode(address)
    print(geocode_result[0]["geometry"]["location"])
    latlng = geocode_result[0]["geometry"]["location"]
    lat = latlng["lat"]
    lng = latlng["lng"]
    return {
        'latitude': lat,
        'longitude': lng
    }
#
# if __name__ == "__main__":
#
#     result = get_distance_and_duration("Sydney Town Hall", "Parramatta, NSW")
#     print(result)
#
#     coordinates = get_coordinates("Tenaya Hall, San Diego, CA 92161")
