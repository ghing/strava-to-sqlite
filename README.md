# strava-to-sqlite

Save Strava activities and activity route GPX data to a SQLite database.

Inspired by the [Dogsheep](https://dogsheep.github.io/) project.

## Assumptions

You've created a Strava API application.

TODO: Document this process.

## Configuration

### `STRAVA_CLIENT_ID`

### `STRAVA_CLIENT_SECRET`

## Installation

```
pip install TK
```

## Authentication

All other commands require fetching an OAuth token. You can do this by running:

```
strava-to-sqlite auth
```

This will create a file called auth.json in your current directory containing the required values. To save the file at a different path or filename, use the `--auth=myauth.json` option.

## Fetch activities

```
strava-to-sqlite strava.db
```

## Development

Clone the repository:

```
git clone TK
```

Change directory to the repository:

```
cd strava-to-sqlite
```

Create a virtualenv:

```
python3 -m venv ./venv
```

Activate the virtualenv:

```
. ./venv/bin/activate
```

Install this package in editable mode:

```
pip install -e .
```

To run the command-line tool sourceing the environment variables from a `.env` file:

```
env $(cat .env | xargs) strava-to-sqlite auth
```

## To do

- Download GPX

- Load data from bulk export
