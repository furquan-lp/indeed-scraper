import requests as req
import re
import json
from urllib.parse import urlencode
from pymongo import MongoClient
from typing import Final

DEFAULT_HEADERS: Final = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Referer': 'https://in.indeed.com/',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1'
}
INDEED_BASE_URL: Final[str] = 'https://in.indeed.com/jobs?'


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


def get_indeed_search_url(keyword: str, location: str, radius: int, offset: int = 0):
    parameters = {'q': keyword, 'l': '' if location == 'None' else location,
                  'filter': 0, 'start': offset, 'radius': radius}
    return INDEED_BASE_URL + urlencode(parameters)


def scrape_indeed_jobs(search_term, location: dict[str, str] | str | None, header_cookie: str):
    jobs = []
    headers = {**DEFAULT_HEADERS, 'Cookie': header_cookie}
    search_location: str = f"{location.get('city')}, {location.get('state')}" if type(
        location) is dict else str(location)
    print('Using', get_indeed_search_url(search_term,
          search_location, 100), '\nHeaders', headers)
    try:
        indeed_jobs_url = get_indeed_search_url(
            search_term, search_location, 100)
        res = req.get(indeed_jobs_url, headers=headers)
        print('response was', res)
        if res.status_code == 200:
            script_tag = re.findall(
                r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', res.text)
            if script_tag is not None:
                json_blob = json.loads(script_tag[0])
                jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
                for index, job in enumerate(jobs_list):
                    if job.get('jobkey') is not None:
                        jobs.append({
                            'id': job.get('jobkey'),
                            'keyword': search_term,
                            'location': location,
                            # 'page': round(offset / 10) + 1 if offset > 0 else 1,
                            'position': index,
                            'company': job.get('company'),
                            'companyRating': job.get('companyRating'),
                            'companyReviewCount': job.get('companyReviewCount'),
                            'jobTitle': job.get('title'),
                            'jobLocationCity': job.get('jobLocationCity'),
                            'jobLocationState': job.get('jobLocationState'),
                            'maxSalary': job.get('extractedSalary').get('max') if job.get('extractedSalary') is not None else 0,
                            'minSalary': job.get('extractedSalary').get('min') if job.get('extractedSalary') is not None else 0,
                            'salaryType': job.get('extractedSalary').get('type') if job.get('extractedSalary') is not None else 'none',
                            'pubDate': job.get('pubDate'),
                        })

                if len(jobs_list) < 10:
                    print('err')
        else:
            print('Error: got response %d' % res.status_code)
            return res.status_code

    except Exception as e:
        print('An error occurred while fetching job IDs:', e)
        return 500
    return jobs
