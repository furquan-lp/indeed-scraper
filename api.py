import requests as req
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from scraper import scrape_indeed_jobs
from typing import Final


class ScraperHeader(BaseModel):
    indeed_header_cookie: str
    indeed_user_agent: str
    logging: bool = False


app = FastAPI()

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
async def root():
    return {'res': '200 OK'}


@app.get('/jobs/{keyword}')
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


@app.get('/jobs/all/{keyword}')
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


@app.get('/jobs/{keyword}/{page}')
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
