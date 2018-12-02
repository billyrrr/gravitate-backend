#!/bin/bash

curl -X POST -H "Content-Type: application/json" -d @frontend_failed_ride_request_form.json https://gravitate-e5d01.appspot.com/rideRequests
