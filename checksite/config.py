"""Configuration info for checksite"""

import re
from typing import Mapping


class Config:
    site_url: str               # the web site to check
    content_regex: re.Pattern   # content must match this regex
    kafka_topic: str
    kafka_servers: str          # comma-separated list: host:port,...
    postgresql_url: str         # any URL accepted by psycopg2

    def __init__(self, environ: Mapping[str, str]):
        self.site_url = environ["CK_SITE_URL"]
        self.content_regex = re.compile(
            environ["CK_CONTENT_REGEX"],
            re.DOTALL)
        self.kafka_topic = environ["CK_KAFKA_TOPIC"]
        self.kafka_servers = environ["CK_KAFKA_SERVERS"]
        self.postgresql_url = environ["CK_POSTGRESQL_URL"]
