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
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper.scraper import scrape_indeed_jobs
from typing import Final


class ScraperHeader(BaseModel):
    indeed_header_cookie: str
    indeed_user_agent: str
    logging: bool = False


class NotFoundMessage(BaseModel):
    detail: str = 'Jobs not found'


app = FastAPI(title='indeed_scraper',
              summary='A fast, exhaustive scraper for Indeed.com',
              version='0.8.0')
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_PAGE_COUNT: Final[int] = 100


def get_server_ip() -> str:
    res = req.get('https://api.ipify.org?format=json').json()
    return res["ip"]


def get_ip_location(ipaddr: str) -> dict[str, str]:
    res = req.get(f'https://ipinfo.io/{ipaddr}/json').json()
    return {'ip': ipaddr,
            'city': res.get('city'),
            'state': res.get('region'),
            'country': res.get('country')}


@app.get('/')
async def root() -> HTMLResponse:
    index_html: str = ''
    try:
        with open('index.html', encoding='utf-8') as f:
            index_html = f.read()
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return HTMLResponse(content=index_html)


@app.get('/jobs/{keyword}',
         summary='Scrape Indeed jobs for keyword',
         description='Scrapes and returns (~10) jobs on the first page from Indeed for the given keyword.',
         response_description='An array of job objects containing keys such as location, maxSalary, minSalary, etc.',
         responses={
             403: {'description': '''Indeed did not allow the scraper to crawl. Possible causes may include user agent
              mismatch and stale cookies.'''},
             404: {'description': 'No jobs were found for the requested keyword and the given location.',
                   'model': NotFoundMessage},
             500: {}
         })
async def find_jobs(keyword: str, request: Request, scraper_header: ScraperHeader,
                    location: dict[str, str] | None = None):
    client_ip: str | None = None if request.client is None else request.client.host
    loc = location
    if client_ip is not None and location is None:
        ip_loc = get_ip_location(client_ip)
        loc = {'city': ip_loc.get('city', ''),
               'state': ip_loc.get('state', '')}
    scraper_result: list | int = scrape_indeed_jobs(keyword, loc, scraper_header.logging,
                                                    cookie=scraper_header.indeed_header_cookie,
                                                    user_agent=scraper_header.indeed_user_agent)
    if type(scraper_result) is int:
        raise HTTPException(status_code=scraper_result, detail="Scraper Error")
    elif not scraper_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Jobs not found")
    else:
        return {'jobs': scraper_result}


@app.get('/jobs/all/{keyword}',
         summary='Scrape *all* Indeed jobs for keyword',
         description='''Crawls through available max_pages Indeed pages (or 100 pages if max_pages is not given) for
         the given keyword, concatenates the jobs found and returns them.''',
         response_description='''A large array of concatenated job objects containing keys such as location, maxSalary,
         minSalary, etc.''',
         responses={
             403: {'description': '''Indeed did not allow the scraper to crawl. Possible causes may include user agent
              mismatch and stale cookies.'''},
             404: {'description': 'No jobs were found for the requested keyword and the given location.',
                   'model': NotFoundMessage},
             500: {}
         })
async def find_all_jobs(keyword: str, request: Request, scraper_header: ScraperHeader,
                        location: dict[str, str] | None = None, max_pages: int = MAX_PAGE_COUNT):
    client_ip: str | None = None if request.client is None else request.client.host
    loc = location
    if client_ip is not None and location is None:
        ip_loc = get_ip_location(client_ip)
        loc = {'city': ip_loc.get('city', ''),
               'state': ip_loc.get('state', '')}

    jobs_found: list[dict] = []
    previus_result: list[dict] = []
    for p in range(1, max_pages, 1):
        scraper_result: list[dict] | int = scrape_indeed_jobs(keyword, loc, scraper_header.logging, page=p,
                                                              cookie=scraper_header.indeed_header_cookie,
                                                              user_agent=scraper_header.indeed_user_agent)
        if scraper_result == previus_result:
            break

        if isinstance(scraper_result, int):
            raise HTTPException(status_code=scraper_result,
                                detail="Scraper Error")
        elif not scraper_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Jobs not found")

        previus_result = scraper_result
        jobs_found += scraper_result

        if len(scraper_result) < 10:
            break

    return {'jobs': jobs_found}


@app.get('/jobs/{keyword}/{page}',
         summary='Scrape Indeed jobs on page for keyword',
         description='Scrapes and returns (~10) jobs on the given page from Indeed for the given keyword.',
         response_description='An array of job objects containing keys such as location, maxSalary, minSalary, etc.',
         responses={
             403: {'description': '''Indeed did not allow the scraper to crawl. Possible causes may include user agent
              mismatch and stale cookies.'''},
             404: {'description': 'No jobs were found for the requested keyword and the given location.',
                   'model': NotFoundMessage},
             500: {}
         })
async def find_n_jobs(keyword: str, page: int, request: Request, scraper_header: ScraperHeader,
                      location: dict[str, str] | None = None):
    client_ip: str | None = None if request.client is None else request.client.host
    loc = location
    if client_ip is not None and location is None:
        ip_loc = get_ip_location(client_ip)
        loc = {'city': ip_loc.get('city', ''),
               'state': ip_loc.get('state', '')}

    scraper_result: list[dict] | int = scrape_indeed_jobs(keyword, loc, scraper_header.logging, page=page,
                                                          cookie=scraper_header.indeed_header_cookie,
                                                          user_agent=scraper_header.indeed_user_agent)

    if isinstance(scraper_result, int):
        raise HTTPException(status_code=scraper_result,
                            detail="Scraper Error")
    elif not scraper_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Jobs not found")
    else:
        return {'jobs': scraper_result}
