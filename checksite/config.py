"""Configuration info for checksite"""

import re
from typing import Mapping


class Config:
    site_url: str               # the web site to check
    content_regex: re.Pattern   # content must match this regex
    kafka_addr: str             # host:port
    postgresql_url: str         # any URL accepted by psycopg2

    def __init__(self, environ: Mapping[str, str]):
        self.site_url = environ["CK_SITE_URL"]
        self.content_regex = re.compile(
            environ["CK_CONTENT_REGEX"],
            re.DOTALL)
        self.kafka_addr = environ["CK_KAFKA_ADDR"]
        self.postgresql_url = environ["CK_POSTGRESQL_URL"]
