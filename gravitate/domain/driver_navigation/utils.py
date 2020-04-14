"""

googlemaps python documentation: https://googlemaps.github.io/google-maps-services-python/docs/
"""
import warnings

import googlemaps

"""
Initialize google maps with key from project "gravitate-testing"
"""
gmaps = googlemaps.Client(key="AIzaSyAdehA_c3snLKJPQ31KRxcMDzxdMGm43eA")


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
    latlng = geocode_result[0]["geometry"]["location"]
    lat = latlng["lat"]
    lng = latlng["lng"]
    return {
        'latitude': lat,
        'longitude': lng
    }


def get_geocode(address=None):
    geocode_result = gmaps.geocode(address)
    # print(geocode_result[0])
    return geocode_result[0]


def get_address(coordinates, result_type="locality"):
    geocode_result = gmaps.reverse_geocode(
        coordinates,
        # location_type="ROOFTOP",
        result_type=result_type
    )

    if len(geocode_result) != 0:
        return geocode_result[0]["formatted_address"]
    else:
        warnings.warn("reverse geocode failed for: {}".format(_coordinates_str(coordinates)))
        return ""


def _coordinates_tuple(d: dict):
    return d["latitude"], d["longitude"],


def _coordinates_str(d: dict):
    return ",".join([str(d["latitude"]), str(d["longitude"])])

#
# if __name__ == "__main__":
#
#     result = get_distance_and_duration("Sydney Town Hall", "Parramatta, NSW")
#     print(result)
#
#     coordinates = get_coordinates("Tenaya Hall, San Diego, CA 92161")
