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

### Extra: Understanding the Cookie

_Disclaimer: Cookie fabrication won't be possible so this section is for educational purposes only. I do not condone
or promote any malicious use of this information._

* When you copy the cookie string you will see something like the following:
```
CTK = "XXXX"
__cf_bm = "XXXXX"
_cfuvid = "XXXXX"
CSRF = "XXXXX"
gonetap = "0"
SHARED_INDEED_CSRF_TOKEN = "XXXXX"
LC = "co=IN"
indeed_rcc = "LV"
INDEED_CSRF_TOKEN = "XXXXX"
LV = "LA=1703877527:CV=1703877527:TS=1703877527"
hpnode = "1"
```
* These are the cookies Indeed saves on your browser when you visit the link https://in.indeed.com/jobs. I'll go over the most important cookies that you _need_ for the scraper to function:
  * `CTK` appears to be a unique hash for the user session, pretty self explanatory
  * `CSRF` and/or `SHARED_INDEED_CSRF_TOKEN` are both used to prevent cross site forgery, you can find more information [here](https://en.wikipedia.org/wiki/Cross-site_request_forgery#Cookie-to-header_token).
  * `__cf_bm` is the Cloudflare bot management cookie to help identify automated traffic (like what we're doing). This is possibly the primary reason for the scraper session expiring so quickly.
  * `_cfuvid` is the Cloudlfare unique visitor id used to rate limit sessions from the same IP address if they don't provide this token. I wouldn't recommend crawling Indeed without this.
  * `LV = "LA=xyz:CV=xyz:TS=xyz"` These appear to be Unix timestamps that match the time the cookie was created, they're probably used (with other tokens) to determine the lifetime of the session. As of January 2024, the session seems to have a pretty short lifespan and it might be extended by manipulating these but you don't need these for the scraper to function.
  * `LC` is a location code. Easy to understand.
  * `hpnode` and `gonetap` appear to be some Indeed-specific preference cookies, they're not important and aren't necessary for the scraper to function as of 2024-01-13