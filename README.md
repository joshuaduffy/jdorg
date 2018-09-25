# jdorg

## Requirements

* `python`
* `node`
* `yarn`

## First step

`pipenv install --dev`

## Running the application
Start the development server

`pipenv run invoke install start`

Build and serve inside an nginx container

`pipenv run invoke clean install build up`

Shut down the container and clean up

`pipenv run invoke down clean`

Run the tests

`pipenv run invoke install test`
