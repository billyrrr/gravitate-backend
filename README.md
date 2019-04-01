# Gravitate Backend

[![Build Status](https://travis-ci.com/billyrrr/gravitate-backend.svg?token=V7MxKCogppX3CT7QjvhV&branch=master)](https://travis-ci.com/billyrrr/gravitate-backend)
[![Coverage Status](https://coveralls.io/repos/github/billyrrr/gravitate-backend/badge.svg?branch=master&t=QGfp9V)](https://coveralls.io/github/billyrrr/gravitate-backend?branch=master)

## Summary
From looking through hundreds of posts in Facebook carpooling groups to spending an unreasonable amount of money on rideshare applications such as Uber and Lyft, finding reliable and affordable transportation to Los Angeles International Airport (LAX) from San Diego can be a nightmare for students looking to return home during school breaks. International students attending UCSD often choose to fly home from LAX instead of San Diego International Airport (SAN) due to the vast difference in airfare, and must decide between largely inefficient modes of transportation such as taking the train or finding rideshare drivers who are willing to make the long trip to the airport. In addition, current rideshare services such as Uber and Lyft do not offer options to carpool with others who are also traveling long distances. To accommodate for these issues our Android application “Gravitate” will provide a platform for users to group up with each other, coordinate long-distance trips to the airport, and split the cost efficiently among the group.

## Gravitate By Team VIBE


David Alexander - Project Manager

Lauren Chang - Business Analyst

Jason Chau - Senior System Analyst

Kenneth Hua - User Experience and Interface Specialist

Sam Huang - Quality Assurance Lead

Andrew Kim - Database Specialist

David Nong - Algorithm Specialist

Billy Rao - Lead Software Architect

Tyler Song - Algorithm Specialist

Leon Wu - Lead Software Developer


## Run the server 
The back end should be deployed in Google App Engine Flexible Environment Python. Make sure 
that App Engine and Firebase are in the same project before proceeding to step 1. 
### Step 1: Firebase Service Account Json
Retrieve Firebase Service Account JSON from Firebase, and set the JSON path and App name
correctly in config.py 
### Step 2: Run Main Scripts
Run main_scripts.py in command lines to generate LAX location and events in the connected 
Firebase Firestore. 
### Step 3: Deploy to Google App Engine
1. Set local project-id to the correct Firebase project with 
```gcloud config set project gravitate-dev ``` (exchange gravitate-dev to desired project-id). 

2. Navigate to directory with app.yaml, run 
```gcloud beta app deploy``` (beta keyword is optional here, we want to add it for better 
debug support in the google cloud console)


## Force Matching for Development Purposes

Gravitate has endpoint ``` /devForceMatch ``` that receives a json. 

### Group All
This is similar to grouping in production environment, where all ride requests are grouped automatically with algorithm written by Tyler. 
```{"operationMode":"all"} ```
You can call it by ```curl -X POST -H "Content-Type: application/json" -d @group_all.json https://gravitate-e5d01.appspot.com/devForceMatch ``` 
in ```gravitate-backend/tests/jsons_to_post_to_endpoint/```

### Group Two
This is for grouping two ride requests. An advantage is that you get to control which two are grouped. Note that 
you should not run two grouping if they are not under the same event. Two ride requests might not be grouped with 
methods other than forceGroupTwo if their "earliest" (defaults to 5 hours before flightLocalTime) and "latest" 
(default to 2 hours before flightLocalTime) range do not overlap. Note that running forceGroupTwo on ride requests 
that do not share the same eventRef (if and only if not on the same day) should raise an exception, but nevertheless 
should not be attempted. Note that if the ride request is already matched to an orbit, you must remove the match first. 
See section RemoveMatch. 

``` {"operationMode":"two", "rideRequestIds":["9msl3amhAj503pAtSjSQod4qy6N26e7h", "PBQILbyLowYlv2WZsDRnPvP61lM6NzoC"]}  ```

You can call it by ```curl -X POST -H "Content-Type: application/json" -d @group_two_2.json https://gravitate-e5d01.appspot.com/devForceMatch ``` 
in ```gravitate-backend/tests/jsons_to_post_to_endpoint/```

### Remove Matching
Before any forcing grouping on two ride requests is done, you should remove matching first. Otherwise, it can 
corrupt relational link and produce bugs that are difficult to detect. Note that this may not succeed sometimes 
if the data is not uniform. In that case, examine the firestore closely to see whether the removal actually succeeded. 

``` {"rideRequestId":"7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU"} ```

You can call it by ```curl -X POST -H "Content-Type: application/json" -d @delete_match.json https://gravitate-e5d01.appspot.com/deleteMatch ``` 
in ```gravitate-backend/tests/jsons_to_post_to_endpoint/```


## Develop Locally

Since the backend project is hosted by Google App Engine Flexible Environment Python, it will take a long set up process to test app locally. Therefore, you may work with submodules that can be tested without exposing to server, and skip all setup process other than "Setup Repository"  and https://cloud.google.com/python/setup. Wheareas, if you want to develop the layers that communicates with client via REST API. You should set up the environment for such testing. 

### Setup Local Environment

Follow the document provided by Google (we are working with Python 3.7/3.6)

Login 

	Username: cse110vibe@gmail.com
	
	Password: miwsag-syWsej-8jydpy

https://cloud.google.com/appengine/docs/flexible/python/quickstart

Make sure that you have deployed and run Hello World on your local machine before moving on to the next steps. DO NOT DEPLOY Hello World to cse110-vibe project, or create a new project to deploy to. 

### Setup Repository

#### mac/Linux

1. Accept invitation to private repository /billyrrr/gravitate-backend 

2. Setup your github account

   https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

3. Open Terminal.

4. Change the current working directory to the location where you want the cloned directory to be made.

5. Type

   ``` git clone https://github.com/billyrrr/gravitate-backend.git ```

6. Press Enter. Your clone will be created. 

#### Windows

1. Accept invitation to private repository /billyrrr/gravitate-backend 

2. Setup your github account

   https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

3. Open Git Bash.

4. Change the current working directory to the location where you want the cloned directory to be made.

5. Type

   ``` git clone https://github.com/billyrrr/gravitate-backend.git ```

6. Press Enter. Your clone will be created. 

### Test App Server Locally

Please skip this section if you do not want to work with REST API related layers. 

https://cloud.google.com/appengine/docs/flexible/python/testing-and-deploying-your-app

```pip3 install WebTest```

```pip3 install nosetest```

run  ```nosetest``` to run tests that are dependent on web app. 

or, (not recommended due to compatibility issue with Python 3),

https://cloud.google.com/appengine/docs/standard/python/tools/using-local-server

## Key Terms

### Timestamp and Datetime
Timestamp has no offset and bijective to UTC time. We are less likely to make any mistake by storing time as timestamp and timezone ID. 
```
Epoch timestamp: 1556773200
Timestamp in milliseconds: 1556773200000
Human time (GMT): Thursday, May 2, 2019 5:00:00 AM
Human time (your time zone): Wednesday, May 1, 2019 10:00:00 PM GMT-07:00
```
One exception is flightLocalTime, which is defined as local time without offset (since offset can be inferred from airport code). 
```"2019-05-02T13:12:00.000"```

## Users

Partially handled by firebase-admin: 
https://firebase.google.com/docs/auth/admin/verify-id-tokens

# Organizing Modules
[Useful Guide](https://stackoverflow.com/questions/12578908/separation-of-business-logic-and-data-access-in-django/12579490#12579490)

## Generate Docs

(TODO: change Makefile)
``` 
sphinx-apidoc -o source/ ../gravitate
python3 -msphinx -b html docs/source docs/build
```

## Reference

<https://help.github.com/articles/cloning-a-repository/#platform-windows>

