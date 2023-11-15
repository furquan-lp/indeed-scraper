from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from scraper import scrape_indeed_jobs


class ScraperHeader(BaseModel):
    indeed_header_cookie: str


app = FastAPI()


@app.get('/')
async def root():
    return {'res': '200 OK'}


@app.get('/jobs/{keyword}', status_code=200)
async def find_jobs(keyword: str, location: dict[str, str], scraper_header: ScraperHeader, response: Response):
    scraper_result: [] | int = scrape_indeed_jobs(
        keyword, location, scraper_header.indeed_header_cookie)
    print(scraper_result)
    if type(scraper_result) is int:
        response.status_code = scraper_result
        return {'error': 'Scraper Error'}
    else:
        return {'keyword': keyword, 'loc': location}
