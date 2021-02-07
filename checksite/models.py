"""Data models for checksite"""

import dataclasses
import datetime
from typing import Optional


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

    # Kafka timestamp for this event (optional because only the consumer
    # cares about this; note that it is NOT NULL in the database schema,
    # which forces the consumer to care)
    timestamp: Optional[datetime.datetime] = None
