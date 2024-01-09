import requests as req
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from scraper import scrape_indeed_jobs


class ScraperHeader(BaseModel):
    indeed_header_cookie: str
    indeed_user_agent: str
    logging: bool | None = None


app = FastAPI()


def get_server_ip():
    res = req.get('https://api.ipify.org?format=json').json()
    return res["ip"]


def get_ip_location(ipaddr: str):
    res = req.get(f'https://ipinfo.io/{ipaddr}/json').json()
    return {'ip': ipaddr,
            'city': res.get('city', ''),
            'state': res.get('region', ''),
            'country': res.get('country', '')}


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
        loc = {'city': ip_loc.get('city'), 'state': ip_loc.get('state')}
    scraper_result: list | int = scrape_indeed_jobs(
        keyword, loc, True, cookie=scraper_header.indeed_header_cookie, user_agent=scraper_header.indeed_user_agent)
    if type(scraper_result) is int:
        raise HTTPException(status_code=scraper_result, detail="Scraper Error")
    elif not scraper_result:
        raise HTTPException(status_code=404, detail="Jobs not found")
    else:
        return {'jobs': scraper_result}
