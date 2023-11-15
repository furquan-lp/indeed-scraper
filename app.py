import os
from dotenv import load_dotenv
from scraper import scrape_indeed_jobs

load_dotenv()
live_cookie = os.environ['INDEED_SCRAPER_COOKIE']

loc = {'city': 'Kolkata', 'state': 'West Bengal'}
js = scrape_indeed_jobs('java', loc, live_cookie)
print('fetched jobs:')
for j in js:
    print(j)

'''
collection_name = db['portfolios']
item_details = collection_name.find()
for item in item_details:
    print(item)
'''
