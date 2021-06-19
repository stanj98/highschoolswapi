# REST API using SWAPI resource

This is a simple application providing a REST
API to an existing API resource called SWAPI ( STAR WARS API - https://swapi.dev/api/).


## Built With
    Django
    Django Rest Framework

## Install

    git clone https://github.com/stanj98/highschoolswapi.git
    
## Create and activate a virtual environment (Windows specific command)

    python3 -m venv <name_of_virtualenv>
    <name_of_virtualenv>\Scripts\activate.bat
    
    
## Install the packages from the requirements text file (ensure that you are in the root project folder)

    pip install -r requirements.txt
    
    
## Run the CRON job

    python manage.py crontab add

## Run the Django server

    python manage.py crontab add

The REST API to the example app is described below.

## Main API

### Request

`GET /api/`

    curl -i -H 'Accept: application/json' http://localhost:8000/api/

### Response

    HTTP 200 OK
    Allow: GET, OPTIONS
    Content-Type: application/json
    Vary: Accept

    {
        "message": "Apart from SWAPI's regular endpoints (https://swapi.dev/api/), use the following features to get a more qualitative and quantiative experience",
        "films info": "Films - http://localhost:8000/api/films/",
        "people info": "People - http://localhost:8000/api/people/",
        "planets info": "Planets - http://localhost:8000/api/planets/",
        "species info": "Species - http://localhost:8000/api/species/",
        "starships info": "Starships - http://localhost:8000/api/starships/",
        "vehicles info": "Vehicles - http://localhost:8000/api/vehicles/",
        "feature 1": "search - search a specified resource by name, title or model (if available)",
        "feature 2": "summarize - get a summarized bio for a specific resource object",
        "feature 3": "get total resource count - get a summarized report on the aggregate total for each resource"
    }
    
    
## Get a resource's whole dataset

### Request

`GET /api/<resource>/`

    curl -i -H 'Accept: application/json' http://localhost:8000/api/people/

### Response

    HTTP 200 OK
    Allow: GET, OPTIONS
    Content-Type: application/json
    Vary: Accept

    {
        "count": 82,
        "next": "https://swapi.dev/api/people/?page=2",
        "previous": null,
        "results": [
            {
                "name": "Luke Skywalker",
                "height": "172",
                "mass": "77",
                "hair_color": "blond",
                "skin_color": "fair",
                "eye_color": "blue",
                "birth_year": "19BBY",
                "gender": "male",
                "homeworld": "https://swapi.dev/api/planets/1/",
                "films": [
                    "https://swapi.dev/api/films/1/",
                    "https://swapi.dev/api/films/2/",
                    "https://swapi.dev/api/films/3/",
                    "https://swapi.dev/api/films/6/"
                ],
                "species": [],
                "vehicles": [
                    "https://swapi.dev/api/vehicles/14/",
                    "https://swapi.dev/api/vehicles/30/"
                ],
                "starships": [
                    "https://swapi.dev/api/starships/12/",
                    "https://swapi.dev/api/starships/22/"
                ],
                "created": "2014-12-09T13:50:51.644000Z",
                "edited": "2014-12-20T21:17:56.891000Z",
                "url": "https://swapi.dev/api/people/1/"
            },
            {
                "name": "C-3PO",
                "height": "167",
                "mass": "75",
                "hair_color": "n/a",
                "skin_color": "gold",
                "eye_color": "yellow",
                "birth_year": "112BBY",
                "gender": "n/a",
                "homeworld": "https://swapi.dev/api/planets/1/",
                "films": [
                    "https://swapi.dev/api/films/1/",
                    "https://swapi.dev/api/films/2/",
                    "https://swapi.dev/api/films/3/",
                    "https://swapi.dev/api/films/4/",
                    "https://swapi.dev/api/films/5/",
                    "https://swapi.dev/api/films/6/"
                ],
                "species": [
                    "https://swapi.dev/api/species/2/"
                ],
                "vehicles": [],
                "starships": [],
                "created": "2014-12-10T15:10:51.357000Z",
                "edited": "2014-12-20T21:17:50.309000Z",
                "url": "https://swapi.dev/api/people/2/"
            },
            ...
        ]
    }
    

## Feature 1: search for a resource (based on name, title or model if available)

### Request

`GET /api/<resource>/?search=<text>`

    curl -i -H 'Accept: application/json' http://localhost:8000/api/people/?search=2

### Response

    HTTP 200 OK
    Allow: GET, OPTIONS
    Content-Type: application/json
    Vary: Accept

    {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "name": "R2-D2",
                "height": "96",
                "mass": "32",
                "hair_color": "n/a",
                ...
            }
        ]
    }

## Feature 2: get a summarized bio-data for a specified resource id

### Request

`GET api/<resource>/:id/summarize/`

    curl -i -H 'Accept: application/json' http://localhost:8000/api/people/1/summarize/

### Response

    HTTP 200 OK
    Allow: GET, OPTIONS
    Content-Type: application/json
    Vary: Accept

    {
        "Luke Skywalker": "Born in 19BBY. male individual with blond hair, fair skin, and weighs 77 kilograms. Also, this person is 172cm tall - get more info at: https://swapi.dev/api/people/1/"
    }
    

## Feature 3: get total count for each resource (summary report)

### Request

`GET /api/total_count/`

    curl -i -H 'Accept: application/json' -X PUT -d 'status=changed3' http://localhost:7000/thing/1

### Response

    HTTP 200 OK
    Allow: GET, OPTIONS
    Content-Type: application/json
    Vary: Accept

    {
            "results": {
                "total people": 82,
                "total planets": 60,
                "total films": 6,
                "total species": 37,
                "total vehicles": 39,
                "total starships": 36
            }
    }

