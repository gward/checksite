"""check site status and send events to Kafka"""

import dataclasses
import os
import time
from typing import Optional

import requests

from . import config


@dataclasses.dataclass
class SiteStatus:
    # the site that was requested (from configuration)
    url: str

    # time to fetch the entire page, in milliseconds
    elapsed: int

    # if we got a network error (eg. connection refused), an error message
    # describing the error
    error: Optional[str]

    # if we got a repsonse, HTTP status code; None on network error
    status: Optional[int]

    # if we got an HTTP response with non-200 status, the first 500
    # characters of the response body
    body_prefix: Optional[str] = None

    # subset of response body that matched content_regex; None if it didn't
    # match or there was any error
    content_match: Optional[str] = None


def check_site(cfg: config.Config) -> SiteStatus:
    # Using requests without an explicit Session always opens a new TCP
    # connection. Normally, I would avoid this behaviour! But for checking
    # availability, it seems worthwhile to ensure that a new connection
    # works. Also, this is likely to run in a new process every time (eg.
    # triggered by cron), so it's not worth the bother of creating a
    # Session.
    t0 = time.time()
    error: Optional[str]
    try:
        resp = requests.get(cfg.site_url)
    except requests.exceptions.RequestException as err:
        error = str(err)
        status = None
    else:
        error = None
        status = resp.status_code

    t1 = time.time()
    body_prefix = content_match = None
    if status == 200:
        if match := cfg.content_regex.search(resp.text):
            content_match = match.group()
    elif status is not None:
        body_prefix = resp.text[0:500]

    return SiteStatus(
        url=cfg.site_url,
        error=error,
        status=status,
        elapsed=round((t1 - t0) * 1000),
        body_prefix=body_prefix,
        content_match=content_match,
    )


def main(environ):
    cfg = config.Config(environ)
    status = check_site(cfg)
    print(dataclasses.asdict(status))


if __name__ == '__main__':
    main(os.environ)
