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

Client development:

`inv install client-dev`

Build and serve inside an nginx container:

`inv install up`

Run the tests:

`inv install test`
