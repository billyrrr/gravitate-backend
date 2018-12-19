# Gravitate Backend

From looking through hundreds of posts in Facebook carpooling groups to spending an unreasonable amount of money on rideshare applications such as Uber and Lyft, finding reliable and affordable transportation to Los Angeles International Airport (LAX) from San Diego can be a nightmare for students looking to return home during school breaks. International students attending UCSD often choose to fly home from LAX instead of San Diego International Airport (SAN) due to the vast difference in airfare, and must decide between largely inefficient modes of transportation such as taking the train or finding rideshare drivers who are willing to make the long trip to the airport. In addition, current rideshare services such as Uber and Lyft do not offer options to carpool with others who are also traveling long distances. To accommodate for these issues our Android application “Gravitate” will provide a platform for users to group up with each other, coordinate long-distance trips to the airport, and split the cost efficiently among the group.

In particular, Gravitate will be useful for students within the same area who are looking to carpool to a shared location. By matching users together that are going to the same destination (LAX), Gravitate will allow users to split the cost of the ride and save up to fifty-percent of the fare as opposed to riding alone. Since Gravitate matches users before the trip to minimize time delays, it also eliminates the need to make numerous stops along the way to pick up random riders; a feature that Uber offers to reduce travel costs but severely compromises time efficiency. As a result of core functionality such as grouping users together and pre-planning trips Gravitate aims to save users both time and money.

Gravitate’s algorithms provide a method for grouping a user with other users based on similar flight times and proximity of pick-up locations by simply having the user upload their itinerary, flight number, or flight time. The user can then expect to be placed in a chat room alongside users with similar travel parameters where they can exchange information, coordinate the Uber or Lyft ride, and get a price estimate for the trip to LAX.  By having the user’s flight details, the app will be able to send the user an update on their ride based on flight delays instantly, before they are even notified by the airline. In addition, the app will give users up-to-date ride information in the chatroom so that users will have ample time to prepare for pick-ups, providing users reassurance on a stressful day of traveling. 

While grouping users together is a main feature of Gravitate, it also provides many extra features that Uber and Lyft cannot match. For example, by requiring that users login with their UCSD Google account, users can feel a sense of security knowing that they won’t be riding with complete strangers. Even if users don’t know know each other well, Gravitate’s user rating system will encourage users to treat each other respect, making as secure as possible. Also, with the ability to allow users to specify the number of bags they are carrying, Gravitate will automatically suggest an UberXL (a larger vehicle) to ensure no user’s belongings are forgotten. Since getting back to school from the airport is just as important as getting to the airport, Gravitate will also provide a function for users with a similar arrival time at LAX to be grouped in rides back to UCSD. These features will make Gravitate the ultimate affordable transportation service for UCSD students. 

Ultimately, Gravitate is an app that aims to streamline the process of transportation for students. With the help of our app, students will no longer have to spend countless hours browsing through bulletin posts for rideshares or have to pay unreasonable amounts of money for an unshared Uber trip to LAX. Gravitate will help students not only save time by connecting them with others who have similar flight times but also save money by splitting the cost of transportation to LAX. With plans of extending from just airports to sporting events, concerts, etc., Gravitate will make every student’s journey more affordable, regardless of where they’re going. 

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

### Other information
Note that the code is held by majic, especially those marked with transactional. Try not change any ```@transactional``` 
decorators if possible. If neccessary, test carefully before and after each change that it does not break anything 
before you change something else. This is mostly because functions decorated by ```@transactional``` commits 
the transaction as they return, almost certainly when having written something with the transaction 
(sometimes it does not commit when you did not write/set/update/etc with the transaction). 


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

###Test App Server Locally

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




## Reference

<https://help.github.com/articles/cloning-a-repository/#platform-windows>

