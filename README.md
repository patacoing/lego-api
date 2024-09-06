![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/patacoing/lego-api/ci.yml)

# Purpose : 

This projet is just a simple rest api built with the Django Rest Framework library in order to learn how to build rest apis with Django.
The data model used is build upon the lego dataset : https://rebrickable.com/downloads/ just to integrate sets and themes.

#  Endpoints : 

- POST /api/themes/bulk => import themes from a csv file into the database
- POST /api/sets/bulk => import sets from a csv file into the database

# Installation : 

## Pre-work

## Python

- Before trying to run the projet, you have to set environment variables as seen in the env.example and you have to start a postgres db

- The project is built using python 3.9
- You first need to create a virtual environment : `python -m venv venv` and then activate it : `source venv/bin/activate`
- You are now able to install the dependencies : `pip install -r requirement.txt`
- Run the server : `python manage.py runserver`

## Docker-compose

TODO
