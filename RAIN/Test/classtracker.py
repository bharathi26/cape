"""
This example shows how to track classes and display statistics at the end of
the script using the web GUI. Snapshots are taken manually. This setup makes
sense with simple batch processing jobs where you want to track memory usage at
certain points in time.
"""

from random import randint

from pympler import web
from pympler.classtracker import ClassTracker

import Messages
from Primitives import Waypoint, WaypointList

from random import random


def create_data(tracker, iterations=100, obj_per_iteration=100):
    objects = []
    for j, x in enumerate(list(range(iterations))):
        # Generate a waypoint list
        wplist = WaypointList("WPL #%i" % j)
        for i, y in enumerate(list(range(obj_per_iteration))):
            wp = Waypoint("Point %i" % i, "%3.5fN" % (52.3 + (random() * 2 - 1)), "%3.5fE" % (52.3 + (random() * 2 -1)))
            wplist.append(wp)
        objects.append(wplist)
#        tracker.create_snapshot()

    return objects


tracker = ClassTracker()

tracker.track_class(Waypoint)
tracker.track_class(WaypointList)
#tracker.track_class(Gamma, trace=True, resolution_level=2)

print ("Create data")
tracker.create_snapshot()
data = create_data(tracker)
print(data)
print ("Drop data")
for item in data:
    del item
del data
tracker.create_snapshot()

print ("Create tenfold data")
tracker.create_snapshot()
data = create_data(tracker, iterations=1000, obj_per_iteration=100)
print ("Drop data")
for item in data:
    del item
del data
tracker.create_snapshot()

web.start_profiler(debug=True, stats=tracker.stats)
