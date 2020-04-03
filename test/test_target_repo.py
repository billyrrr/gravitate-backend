import pytest
from gravitate.algo_server import TargetRepo
from gravitate.domain.target import Target


def test_add():
    repo = TargetRepo()
    target_1 = Target.new(
        doc_id="target_1",
        earliest_arrival=102,
        latest_arrival=109,
        earliest_departure=2,
        latest_departure=9,
        r_ref="rider_1",
        from_lat=22,
        from_lng=99,
        to_lat=122,
        to_lng=199
    )
    repo.add(target_1)

    target_2 = Target.new(
        doc_id="target_2",
        earliest_arrival=100,
        latest_arrival=101,
        earliest_departure=0,
        latest_departure=1,
        r_ref="rider_2",
        from_lat=22,
        from_lng=99,
        to_lat=122,
        to_lng=199
    )
    t = repo.add(target_2)
    assert t is None

    target_3 = Target.new(
        doc_id="target_3",
        earliest_arrival=103,
        latest_arrival=107,
        earliest_departure=3,
        latest_departure=7,
        r_ref="rider_1",
        from_lat=22,
        from_lng=99,
        to_lat=122,
        to_lng=199
    )
    t = repo.add(target_3)
    assert t is None

    target_4 = Target.new(
        doc_id="target_4",
        earliest_arrival=103,
        latest_arrival=107,
        earliest_departure=3,
        latest_departure=7,
        r_ref="rider_3",
        from_lat=22,
        from_lng=99,
        to_lat=122,
        to_lng=199
    )
    t = repo.add(target_4)
    assert t == 'Target/target_1'
