import os
import json
from sys import stderr
from dotenv import load_dotenv
from scraper import scrape_indeed_jobs

load_dotenv()
live_cookie = os.environ['INDEED_SCRAPER_COOKIE']
location_json = os.environ['INDEED_SCRAPER_LOCATION_JSON']
keywords_json = os.environ['INDEED_SCRAPER_KEYWORDS_JSON']


def load_json_file(json_file: str):
    try:
        with open(json_file, encoding='utf-8') as jfile:
            return json.loads(jfile.read())
    except FileNotFoundError:
        print(
            f'Error: File {os.path.realpath(__file__)}/{json_file} not found.', file=stderr)


locations: dict[str, list[str]] = load_json_file(location_json)
states: list[str] = locations.get('states', [])
cities: list[str] = locations.get('capitalCities', [])
keywords: list[str] = load_json_file(keywords_json)


for keyword in keywords:
    for state, city in zip(states, cities):
        print(f'Searching "{keyword}" for {city}, {state}')

""" loc = {'city': '', 'state': 'West Bengal'}
js = scrape_indeed_jobs('java', loc, True, cookie=live_cookie,
                        user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0')
print('fetched jobs:')

if isinstance(js, int):
    print('Error', js)
else:
    for j in js:
        print(j) """

'''
collection_name = db['portfolios']
item_details = collection_name.find()
for item in item_details:
    print(item)
'''
