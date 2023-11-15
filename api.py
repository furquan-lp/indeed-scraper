from fastapi import FastAPI
from pydantic import BaseModel
from scraper import scrape_indeed_jobs


class ScraperHeader(BaseModel):
    indeed_header_cookie: str


app = FastAPI()


@app.get('/')
async def root():
    return {'res': '200 OK'}


@app.get('/jobs/{keyword}')
async def find_jobs(keyword: str, location: dict[str, str], scraper_header: ScraperHeader):
    scraper_result: [] | int = scrape_indeed_jobs(
        keyword, location, scraper_header.indeed_header_cookie)
    print(scraper_result)
    return {'keyword': keyword, 'loc': location}
