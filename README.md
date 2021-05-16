# strava-to-sqlite

Save Strava activities and activity route GPX data to a SQLite database.

Inspired by the [Dogsheep](https://dogsheep.github.io/) project.

## Assumptions

You have SQLite version 3.24 or later.

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
pip install git+https://github.com/ghing/strava-to-sqlite.git
```

If you want to download GPX files for activities, you'll have to install the browsers that [Playwright](https://playwright.dev/) uses for browser automation. The Playwright package should have been installed when you installed this package, so the only additional step is to run:

```
playwright install
```

## Authentication

All other commands require fetching an OAuth token. You can do this by running:

```
strava-to-sqlite auth
```

This will create a file called auth.json in your current directory containing the required values. To save the file at a different path or filename, use the `--auth=myauth.json` option.

## Fetch activities

```
strava-to-sqlite activities strava.db
```

By default this will fetch all activities since the most recent one already in the database.

If you want to empty your database table and re-download all the activities, run:

```
strava-to-sqlite activities --all-activities --truncate strava.db
```

## Fetch GPX tracks for activities

```
strava-to-sqlite activity-gpx strava.db
```

By default it loads all GPX files corresponding to activities retrieved using the `activities` subcommand.

This also saves the downloaded GPX files in a `cache/gpx` directory. You can specify the parent cache directory with the `--cache-dir` option.

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

- Load data from [bulk export](https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export#Bulk)

## Similar projects

- [strava-offline](https://pypi.org/project/strava-offline/)
