# jdorg

## Requirements

* `python`
* `pipenv`
* `node`
* `yarn`

## First step

1. Create a new virtual environment via `pipenv --three`
2. Install the dependencies via `pipenv install --dev`

Enter a shell session via `pipenv shell` to run `inv` commands (or prepend `pipenv run` to all subsequent `inv` commands).

## List invoke commands

`inv --list`

## Common commands

Start the development server:

`inv install start`

Build and serve inside an nginx container:

`inv clean install build up`

Shut down the container and clean up:

`inv down clean`

Run the tests:

`inv install test`
