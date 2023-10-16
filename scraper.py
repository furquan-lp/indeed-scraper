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


def get_indeed_search_url(keyword, location, radius, offset=0):
    parameters = {'q': keyword, 'l': location,
                  'filter': 0, 'start': offset, 'radius': radius}
    return 'https://in.indeed.com/jobs?' + urlencode(parameters)


job_ids = []
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
    'TE': 'trailers'
}
keyword = 'python'
location = {'city': 'Patna', 'state': 'Bihar'}
print('Using', get_indeed_search_url(
    keyword, f"{location.get('city')}, {location.get('state')}", 100))

for offset in range(0, 1010, 10):
    try:
        indeed_jobs_url = get_indeed_search_url(
            keyword, f"{location.get('city')}, {location.get('state')}", 100, offset)
        res = req.get(indeed_jobs_url, headers=headers)

        if res.status_code == 200:
            script_tag = re.findall(
                r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', res.text)
            if script_tag is not None:
                json_blob = json.loads(script_tag[0])
                jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
                for index, job in enumerate(jobs_list):
                    if job.get('jobkey') is not None:
                        job_ids.append(job.get('jobkey'))

                if len(jobs_list) < 10:
                    break

    except Exception as e:
        print('An error occurred while fetching job IDs:', e)

print(job_ids)
