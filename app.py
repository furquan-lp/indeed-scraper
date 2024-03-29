"""
This file is part of indeed_scraper.

indeed_scraper is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

indeed_scraper is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with indeed_scraper. If not, see
<https://www.gnu.org/licenses/>. 
"""

import os
import json
from sys import stderr
from dotenv import load_dotenv
from scraper.scraper import scrape_indeed_jobs
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()
live_cookie = os.environ['INDEED_SCRAPER_COOKIE']
user_agent = os.environ['INDEED_SCRAPER_USER_AGENT']
location_json = os.environ['INDEED_SCRAPER_LOCATION_JSON']
keywords_json = os.environ['INDEED_SCRAPER_KEYWORDS_JSON']


def load_json_file(json_file: str):
    try:
        with open(json_file, encoding='utf-8') as jfile:
            return json.loads(jfile.read())
    except FileNotFoundError:
        print(
            f'Error: File {os.path.realpath(__file__)}/{json_file} not found.', file=stderr)


def count_db_jobs(db: Database, keywords: list[str]) -> int:
    total: int = 0
    for keyword in keywords:
        collection = db[keyword]
        item_details = collection.find()
        for item in item_details:
            num_jobs = len(item.get("jobs", ""))
            print(
                f'{num_jobs} \'{keyword}\' jobs in {item["city"]}, {item["state"]}')
            total += num_jobs
    return total


client: MongoClient = MongoClient(
    os.environ['INDEED_SCRAPER_DB_URI'], tls=True, tlsCertificateKeyFile=os.environ['INDEED_SCRAPER_DB_CERT'])

try:
    client.admin.command('ping')
    print('Pinged database. Successfully connected to MongoDB.')
except Exception as e:
    print(f'Couldn\'t connect to the database: {e}', file=stderr)

db = client.indeed_scrape
locations: dict[str, list[str]] = load_json_file(location_json)
states: list[str] = locations.get('states', [])
cities: list[str] = locations.get('capitalCities', [])
keywords: list[str] = load_json_file(keywords_json)
skip: list[str] = load_json_file('skip.json')

for keyword in keywords:
    current_collection = db[keyword]
    for state, city in zip(states, cities):
        if state in skip or city in skip:
            print(f'Skipping {city}, {state}')
            continue

        print(f'Searching "{keyword}" for {city}, {state}...')

        jobs_found: list[dict] = []
        previus_result: list[dict] = []
        for p in range(1, 100, 1):
            scraper_result = scrape_indeed_jobs(keyword, {'city': city, 'state': state}, False, page=p,
                                                cookie=live_cookie, user_agent=user_agent)
            if scraper_result == previus_result:
                break

            if isinstance(scraper_result, int):
                print(
                    f'Breaking at page {p} for {city}, {state}. Scraper error: {scraper_result}.', file=stderr)
                break
            elif not scraper_result:
                print(
                    f'Breaking at page {p} for {city}, {state}. No jobs found: {scraper_result}.', file=stderr)
                break

            previus_result = scraper_result
            jobs_found += scraper_result

            if len(scraper_result) < 10:
                break

        document = {
            'city': city,
            'state': state,
            'jobs': jobs_found
        }
        current_collection.insert_one(document)

print(count_db_jobs(db, keywords))

client.close()
