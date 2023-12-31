# indeed-scraper
Python project to scrape Indeed data and catalog it on a fully editable web dashboard

## Scraper Instructions

* The `scrape_indeed_jobs` function scrapes Indeed.com for the given search term and location using the given client
cookie
* `location` here is a dictionary with `city` and `state` as keys
* The `extra_headers` kwarg has two parts:
  * The `cookie` is part of the request header sent to Indeed and it needs to be a live cookie, see below for
instructions on how to find it
  * The `user_agent` is also part of the request header and it needs to match the live cookie, see below for
instructions on how to find it
  * If either of the above aren't provided, default values will be used
  * Be warned however, cookie fabrication isn't on the list yet and the default user agent will probably not work
* `scrape_indeed_jobs` returns a list of dictionaries containing individual job entries with the company, position,
salary, etc.

## Finding the Indeed Cookie

* The extra_header kwarg for `scrape_indeed_jobs` needs to contain the cookie string with Indeed cookies from a live
session
* To find yours first open the developer console and navigate to https://indeed.com/jobs
* Find the first GET request for indeed.com, in.indeed.com, etc. and copy it in cURL syntax, it'll look something like
this:
```
curl 'https://in.indeed.com/?from=jobsearch-empty-whatwhere' --compressed -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' -H 'Accept-Language: en-GB,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Cookie: XXXXXXXXXXXXXXXXXXXXXXXX' -H 'Upgrade-Insecure-Requests: 1' -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: none' -H 'Sec-Fetch-User: ?1' -H 'Sec-GPC: 1' -H 'TE: trailers'
```
* Copy the entire value for `Cookie: ` and pass it as the `cookie`

## Finding Your User Agent String

* The user agent string must match the session the above live cookie was obtained from
* To find it follow the above instructions exactly
* Then copy the value for `User-Agent` and pass it as the `user_agent`