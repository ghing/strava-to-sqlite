"""Package installation"""

import os
from setuptools import setup

VERSION = "0.0.2"


def get_long_description():
    """Get long package description from README"""
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as readme_fp:
        return readme_fp.read()


setup(
    name="strava-to-sqlite",
    description="Save data from Strava to a SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Geoff Hing",
    url="https://github.com/ghing/strava-to-sqlite",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["strava_to_sqlite"],
    entry_points="""
        [console_scripts]
        strava-to-sqlite=strava_to_sqlite.cli:cli
    """,
    install_requires=[
        "click~=7.1.0",
        "fiona~=1.8.19",
        "playwright~=1.10.0",
        "requests~=2.25.1",
        "requests-oauthlib~=1.3.0",
        "shapely~=1.7.1",
        "sqlite-utils~=3.6",
    ],
    extras_require={
        "dev": [
            "pre-commit~=2.12.1",
            "pylint~=2.8.2",
        ],
    },
)
