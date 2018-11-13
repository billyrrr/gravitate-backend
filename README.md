# Gravitate Backend

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

####mac/Linux

1. Accept invitation to private repository /billyrrr/gravitate-backend 

2. Setup your github account

   https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

3. Open Terminal.

4. Change the current working directory to the location where you want the cloned directory to be made.

5. Type

   ``` git clone https://github.com/billyrrr/gravitate-backend.git ```

6. Press Enter. Your clone will be created. 

####Windows

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

## Reference

<https://help.github.com/articles/cloning-a-repository/#platform-windows>

