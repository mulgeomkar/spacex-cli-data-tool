import click
import requests
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
from database import SpaceXDatabase
from models import Launch

CACHE_DIR = Path("cache")
OUTPUT_DIR = Path("outputs")
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

class SpaceXAPI:
    BASE_URL = "https://api.spacexdata.com/v4"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SpaceX-CLI-Tool/1.0',
            'Accept': 'application/json'
        })

    def get_launches(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Fetch launches from SpaceX API with pagination and retry/backoff"""
        url = f"{self.BASE_URL}/launches/query"
        payload = {
            "options": {
                "limit": limit,
                "offset": offset,
                "sort": {"flight_number": "desc"},
                "populate": ["rocket", "launchpad"]
            }
        }
        tries = 0
        while tries < 5:
            try:
                response = self.session.post(url, json=payload)
                response.raise_for_status()
                return response.json()["docs"]
            except requests.exceptions.HTTPError as err:
                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 1))
                    time.sleep(wait * (2 ** tries))
                else:
                    raise
            tries += 1
        raise Exception("Unable to fetch data after retries.")

@click.group()
def cli():
    pass

@cli.command()
@click.option('--param', default=50, help='Number of launches to fetch')
def fetch(param):
    """Fetch launches and save to cache + normalized SQLite DB"""
    api = SpaceXAPI()
    db = SpaceXDatabase()
    launches_raw = api.get_launches(limit=param)
    # Cache raw
    cache_path = CACHE_DIR / f"launches_raw_{param}.json"
    with open(cache_path, "w") as f:
        json.dump(launches_raw, f, indent=2)
    # Save one sample payload
    with open(OUTPUT_DIR / "sample_fetch.json", "w") as f:
        json.dump(launches_raw[:1], f, indent=2)
    # Normalize and store in DB
    launches = [Launch.from_api_data(x) for x in launches_raw]
    db.insert_launches(launches)
    click.echo(f"Fetched and saved {len(launches)} launches.")

@cli.command()
@click.option('--filter', default="", help="Filter, e.g. success:true")
@click.option('--limit', default=5, help="Limit results")
def query(filter, limit):
    """Query DB for launches matching filters, pretty print and save JSON"""
    db = SpaceXDatabase()
    filters = {}
    if filter:
        for f in filter.split(","):
            k, v = f.split(":", 1)
            # Support boolean conversion
            if v.lower() in ["true", "false"]:
                v = v.lower() == "true"
            filters[k] = v
    launches = db.query_launches(filters, limit=limit)
    launches_json = [l.to_dict() for l in launches]
    print(json.dumps(launches_json, indent=2))
    # Save sample query result
    with open(OUTPUT_DIR / "sample_query.json", "w") as f:
        json.dump(launches_json, f, indent=2)

if __name__ == "__main__":
    cli()
