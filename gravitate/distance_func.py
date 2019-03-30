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