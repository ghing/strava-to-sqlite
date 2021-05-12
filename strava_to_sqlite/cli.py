from functools import partial
import json
import os

import click
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
