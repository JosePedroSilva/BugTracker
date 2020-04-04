# Bug tracker

  

Bug tracker with multi level user and ticket management system

  

## Demo

  

Deployed:

https://bug-tracker-js.herokuapp.com/

  

```

Test users:

	username: admin // password: admin

	username: manager // password: manager

	username: user // password: user

```

  

## Requirements

Python 3.6+, python-pip, virtualenv

  
  

## Features

  

Some features included in this demo application are:

  

### Ticket System

  Ticket creation system that can be managed by:
  
	*Priority;
	*Date;
	*User reporter and owner;
	*Team;
	*Status;
	
  Users can comment and update ticket information

### Users

  

There are three user level:

*User: Can create tickets and comment on tickets;

*Manager: Can assign the tickets and change the status

*Admin: Create new users, change current user access level and information, delete users, change and add new teams and ticket topics 

  
  

## Getting Started

  

First, clone this repo

  

```

$ git clone https://github.com/JosePedroSilva/BugTracker

$ cd BugTracker

```

  

Create virtual environment

  

```

$ python3 -m venv env

$ source env/bin/activate

(env) $ _

```

  

Install all necessary dependencies

  

```

$ pip install -r requirements.txt

```

Set the flask environment

For windows use set command

```

(env) $ export FLASK_APP=bugTracker.py

```

Run the application:

```

(env) $ flask run

```

Access url to see web app

```

http://localhost:5000/

```