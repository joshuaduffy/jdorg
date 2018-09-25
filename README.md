# jdorg

## Requirements

* `python`
* `node`
* `yarn`

## First step

1. Create a new virtual environment via `pipenv --three`
2. Install the dependencies via `pipenv install --dev`

## Running the application

Firstly, enter a shell session via `pipenv shell` to run `invoke` commands.

Start the development server

`inv install start`

Build and serve inside an nginx container

`inv clean install build up`

Shut down the container and clean up

`inv down clean`

Run the tests

`inv install test`
