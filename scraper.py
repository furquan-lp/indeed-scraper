import requests as req
import re
import json
from urllib.parse import urlencode


def get_current_ip():
    res = req.get('https://api.ipify.org?format=json').json()
    return res["ip"]


def get_location_ip(ipaddr):
    res = req.get(f'https://ipinfo.io/{ipaddr}/json').json()
    return {'ip': ipaddr,
            'city': res.get('city'),
            'state': res.get('region'),
            'country': res.get('country')
            }


def get_indeed_search_url(keyword, location, offset=0):
    parameters = {'q': keyword, 'l': location, 'filter': 0, 'start': offset}
    return 'https://in.indeed.com/jobs?' + urlencode(parameters)


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/118.0'}

job_ids = []
keyword = 'python'
location = get_location_ip(get_current_ip())
print(get_indeed_search_url(
    keyword, f"{location.get('city')}, {location.get('state')}"))
