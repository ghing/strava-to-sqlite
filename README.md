# strava-to-sqlite

Save Strava activities and activity route GPX data to a SQLite database.

Inspired by the [Dogsheep](https://dogsheep.github.io/) project.

## Assumptions

You've created a Strava API application.

TODO: Document this process.

You have python built with the ability to load the SQLite extensions. I use pyenv to install my Python versions and this is what I had to do on Ubuntu:

```
CONFIGURE_OPTS=--enable-loadable-sqlite-extensions pyenv install 3.9.4
```

On a Mac with Homebrew, I also had to point the Python build process at the Homebrew version of SQLite instead of the system one:

```
LDFLAGS="-L/usr/local/opt/sqlite/lib" CPPFLAGS="-I/usr/local/opt/sqlite/include" CONFIGURE_OPTS=--enable-loadable-sqlite-extensions pyenv install 3.9.4
```

## Configuration

Configuration is through environment variables.

### `STRAVA_CLIENT_ID`

### `STRAVA_CLIENT_SECRET`

### `STRAVA_USERNAME`

### `STRAVA_PASSWORD`

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

- Load GPX into database

- Load data from bulk export

## Similar projects

- [strava-offline](https://pypi.org/project/strava-offline/)
