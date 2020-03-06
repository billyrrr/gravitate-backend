from haversine import haversine
from math import inf

#example params
# params_a = [earliest, latest, lat, long]

def time_constraint( a_earliest:int, a_latest:int, b_earliest:int, b_latest:int ):
    earliest_start = max(a_earliest, b_earliest)
    latest_start = min(a_latest, b_latest)
    return earliest_start <= latest_start

## Assumptions we are given lat long, earliest, latest
def distance_func( params_a:list, params_b:list, max_dist:float = 500):
    #Readability purposes
    a_coord = (params_a[2], params_a[3])
    b_coord = (params_b[2], params_b[3])

    a_earliest = params_a[0]
    a_latest = params_a[1]
    b_earliest = params_b[0]
    b_latest = params_b[1]

    dist = haversine(a_coord, b_coord, unit="km")
    # Time Constraint
    if ( time_constraint(a_earliest, a_latest, b_earliest, b_latest) and dist <= max_dist ):
        return dist
    else:
        return inf


def edge_weight( params_a:dict, params_b:dict, max_dist:float = 500):

    a_from = (params_a["from_lat"], params_a["from_lng"])
    b_from = (params_b["from_lat"], params_b["from_lng"])
    dist_from = haversine(a_from, b_from, unit="km")

    a_to = (params_a["to_lat"], params_a["to_lng"])
    b_to = (params_b["to_lat"], params_b["to_lng"])
    dist_to = haversine(a_to, b_to, unit="km")

    dep = time_constraint(
        params_a["earliest_departure"], params_a["latest_departure"],
        params_b["earliest_departure"], params_b["latest_departure"])

    arr = time_constraint(
        params_a["earliest_arrival"], params_a["latest_arrival"],
        params_b["earliest_arrival"], params_b["latest_arrival"]
    )

    if dep and arr and dist_from <= max_dist and dist_to <= max_dist:
        return dist_from + dist_to
    else:
        return inf
