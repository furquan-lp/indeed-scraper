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

import requests as req
import re
import json
import logging
from sys import stderr
from urllib.parse import urlencode
from typing import Final
from http import HTTPStatus

DEFAULT_USER_AGENT: Final[str] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
DEFAULT_HEADERS: Final = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Referer': 'https://in.indeed.com/?from=jobsearch-empty-whatwhere',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
    'TE': 'trailers'
}
INDEED_BASE_URL: Final[str] = 'https://in.indeed.com/jobs?'
global_logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s  %(levelname)s: %(message)s')


def get_indeed_url(keyword: str, location: str, radius: int, offset: int = 0) -> str:
    parameters = {'q': keyword, 'l': '' if location == 'None' else location,
                  'filter': 0, 'start': offset, 'radius': radius}
    return INDEED_BASE_URL + urlencode(parameters)


def scrape_indeed_jobs(search_term, location: dict[str, str] | str | None, log: bool = False,
                       logfilename: str = f'{__name__}.log', page: int = 1, **extra_headers: str) -> int | list[dict]:
    jobs = []
    headers = {'User-Agent': extra_headers.get('user_agent', DEFAULT_USER_AGENT),
               **DEFAULT_HEADERS, 'Cookie': extra_headers.get('cookie', '')}
    search_location: str = f"{location.get('city')}, {location.get('state')}" if type(
        location) is dict else str(location)
    offset = abs(10 * (page - 1))

    logfile_handler = logging.FileHandler(logfilename)
    logfile_handler.setFormatter(formatter)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    if log:
        global_logger.setLevel(logging.INFO)
        if not global_logger.handlers:
            global_logger.addHandler(logfile_handler)
            global_logger.addHandler(stdout_handler)
    else:
        global_logger.setLevel(logging.ERROR)
        for h in global_logger.handlers:
            h.close()
            global_logger.removeHandler(h)

    global_logger.info(
        f'Using {get_indeed_url(search_term, search_location, 100, offset)} \nHeaders {headers}')

    try:
        indeed_jobs_url = get_indeed_url(
            search_term, search_location, 100, offset)
        res = req.get(indeed_jobs_url, headers=headers)
        if res.status_code == HTTPStatus.OK:
            script_tag = re.findall(
                r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', res.text)
            if script_tag and script_tag is not None:
                json_blob = json.loads(script_tag[0])
                jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
                for index, job in enumerate(jobs_list):
                    if job.get('jobkey') is not None:
                        jobs.append({
                            'id': job.get('jobkey'),
                            'keyword': search_term,
                            'location': location,
                            # 'page': page,
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
            else:
                return HTTPStatus.NOT_FOUND
        else:
            global_logger.error('Error: got response %d' % res.status_code)
            return res.status_code
    except Exception as e:
        global_logger.error(f'An error occurred while fetching job IDs: {e}')
        return HTTPStatus.INTERNAL_SERVER_ERROR
    return jobs
