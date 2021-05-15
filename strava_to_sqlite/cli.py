from functools import partial
import json
import os
from pathlib import Path
import re
import shutil

import click
from playwright.sync_api import sync_playwright
import requests
from requests_oauthlib import OAuth2Session
from sqlite_utils import Database

from strava_to_sqlite.auth_http_server import (
    AuthHTTPRequestHandler,
    DataSavingHTTPServer,
)


def save_token(token, json_path):
    """Save an OAuth token to a JSON file"""
    with open(json_path, "w") as outf:
        outf.write(json.dumps(token))

@click.group()
@click.version_option()
def cli():
    """Save data from Strava to a SQLite database"""

@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def auth(auth):
    """Save authentication credentials to a JSON file"""
    client_id = os.environ["STRAVA_CLIENT_ID"]
    client_secret = os.environ["STRAVA_CLIENT_SECRET"]

    scope = [
        "activity:read_all",
    ]
    oauth = OAuth2Session(
        client_id,
        redirect_uri="http://localhost:8080/",
        scope=scope
    )
    authorization_url, state = oauth.authorization_url(
        "https://www.strava.com/oauth/authorize",
        approval_prompt="force"
    )
    print(f"Please visit {authorization_url}")

    host = ''
    port = 8080
    server = DataSavingHTTPServer((host, port), AuthHTTPRequestHandler)
    server.serve_forever()
    # Get an access token
    # See https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#web-application-flow
    # See also https://developers.strava.com/docs/getting-started/
    token = oauth.fetch_token(
        "https://www.strava.com/oauth/token",
        client_id=client_id,
        client_secret=client_secret,
        code=server.get_app_data("authorization_code"),
        # This is required to get this to work with Strava's endpoint
        include_client_id=True
    )
    save_token(token, auth)


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def activities(db_path, auth):
    """Fetch activities feed"""
    client_id = os.environ["STRAVA_CLIENT_ID"]
    client_secret = os.environ["STRAVA_CLIENT_SECRET"]

    with open(auth) as f:
        token = json.load(f)

    # See https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html
    # and https://developers.strava.com/docs/authentication/#refreshingexpiredaccesstokens
    extra = {
        "client_id": client_id,
        "client_secret": client_secret,
    }
    refresh_url = "https://www.strava.com/oauth/token"

    token_saver = partial(save_token, json_path=auth)

    client = OAuth2Session(
        client_id,
        token=token,
        auto_refresh_url=refresh_url,
        auto_refresh_kwargs=extra,
        token_updater=token_saver
    )

    activities = []
    page = 1
    while True:
        resp = client.get(
            "https://www.strava.com/api/v3/athlete/activities",
            params={
                "page": page,
            }
        )
        if resp.status_code != 200:
            break

        activities += resp.json()
        page += 1

    # TODO: Handle getting only recent values.
    db = Database(db_path)
    db["activities"].insert_all(activities, pk="id", truncate=True)

def slugify(val, sep="_"):
    """Create a slug appropriate for use in filenames"""
    # Convert to lower case
    slugified = val.lower()

    # Remove special characters
    slugified = re.sub(r"[#'\",\-]", "", slugified)

    # Replace whitespace with separator and remove repeated whitespace
    slugified = re.sub(r"\s+", sep, slugified)

    return slugified

def gpx_filename(activity):
    """Get a standardized filename for a GPX file for an activity"""
    # Get the local activity date in YYYYMMDD format
    activity_date_slug = activity["start_date_local"][:10].replace("-", "")

    return f"{activity_date_slug}_{activity['id']}_{slugify(activity['name'])}.gpx"

def download_gpx(playwright, activities, username, password, user_data_dir, gpx_dir):
    """Use playwright to download a GPX file"""
    context = playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        accept_downloads=True,
    )
    # Open new page
    page = context.new_page()

    # Go to https://www.strava.com/
    page.goto("https://www.strava.com/")

    # Click text=Log In
    page.click("text=Log In")
    # assert page.url == "https://www.strava.com/login"

    # Click :nth-match(div:has-text("Log In Log in using Facebook Log in using Google Sign in with Apple Or log in wi"), 2)
    page.click(":nth-match(div:has-text(\"Log In Log in using Facebook Log in using Google Sign in with Apple Or log in wi\"), 2)")

    # Click [placeholder="Your Email"]
    page.click("[placeholder=\"Your Email\"]")
    # Fill [placeholder="Your Email"]
    page.fill("[placeholder=\"Your Email\"]", username)
    # Press Tab
    page.press("[placeholder=\"Your Email\"]", "Tab")
    # Fill [placeholder="Password"]
    page.fill("[placeholder=\"Password\"]", password)
    # Click button:has-text("Log In")
    page.click("button:has-text(\"Log In\")")
    # assert page.url == "https://www.strava.com/dashboard"

    for activity in activities:
        gpx_path = gpx_dir / gpx_filename(activity)

        # TODO: Support forcing the re-download of the activity
        if gpx_path.exists():
            # Don't re-download a GPX file that already exists
            continue

        # Go to page for activities 
        page.goto(f"https://www.strava.com/activities/{activity['id']}")

        # Click [aria-label="Actions"]
        page.click("[aria-label=\"Actions\"]")
        # Click text=Export GPX
        with page.expect_download() as download_info:
            page.click("text=Export GPX")

        download = download_info.value
        path = download.path()

        shutil.copyfile(path, gpx_path)

    # ---------------------
    context.close()

    # TODO: Load files into the database

@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
@click.option(
    "-c",
    "--cache-dir",
    type=click.Path(file_okay=False, dir_okay=True, allow_dash=False),
    default="cache",
    help="Path to save downloaded GPX files to, defaults to cache",
)
@click.option(
    "-i",
    "--activity-id",
    type=int,
    multiple=True,
    default=[],
    help="Activity ID of activity GPX to download",
)
def activity_gpx(db_path, auth, cache_dir, activity_id=[]):
    """Download GPX for an activity or all activities."""
    STRAVA_USERNAME = os.environ["STRAVA_USERNAME"]
    STRAVA_PASSWORD = os.environ["STRAVA_PASSWORD"]

    cache_dir= Path(cache_dir)
    user_data_dir = cache_dir / "playwright_user_data"
    gpx_dir = cache_dir / "gpx"
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(gpx_dir, exist_ok=True)

    db = Database(db_path)

    if len(activity_id) != 0:
        # User specified explicit activity IDs 

        # HACK: AFAIK Python SQLite parameter replacement only supports
        # individual values, so since we have a list of IDs, we need to
        # build up the placeholder string based on the number of values
        # in our list of activity IDs. I think this is relatively safe
        # since we're not using string interpolation to insert values
        # into the SQL, just a certain number of `?` placeholders.
        in_placeholder = ", ".join(["?" for i in range(len(activity_id))])
        activities = list(db["activities"].rows_where(
            f"id IN ({in_placeholder})",
            activity_id,
            select="id, name, start_date_local",
        ))

    else:
        # User didn't specify activity IDs. Download them all.
        activities = list(db["activities"].rows_where(
            select="id, name, start_date_local"
        ))

    with sync_playwright() as playwright:
        download_gpx(playwright, activities, STRAVA_USERNAME, STRAVA_PASSWORD, user_data_dir, gpx_dir)
