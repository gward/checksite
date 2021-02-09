"""Configuration info for checksite"""

import re
from typing import Mapping


class Config:
    site_url: str               # the web site to check
    content_regex: re.Pattern   # content must match this regex
    kafka_topic: str
    kafka_servers: str          # comma-separated list: host:port,...
    kafka_ssl: str              # <ca-cert> <client-cert> <client-key>
    postgresql_url: str         # any URL accepted by psycopg2

    def __init__(self, environ: Mapping[str, str]):
        self.site_url = environ["CK_SITE_URL"]
        self.content_regex = re.compile(
            environ["CK_CONTENT_REGEX"],
            re.DOTALL)
        self.kafka_topic = environ["CK_KAFKA_TOPIC"]
        self.kafka_servers = environ["CK_KAFKA_SERVERS"]
        self.kafka_ssl = environ["CK_KAFKA_SSL"]
        self.postgresql_url = environ["CK_POSTGRESQL_URL"]

    def get_kafka_config(self) -> Mapping[str, str]:
        """Return config settings needed for confluent_kafka clients."""
        result = {'bootstrap.servers': self.kafka_servers}
        if ssl_bits := self.kafka_ssl.split(None, 2):
            (ca_cert, client_cert, client_key) = ssl_bits
            result.update({
                'security.protocol': 'ssl',
                'ssl.ca.location': ca_cert,
                'ssl.certificate.location': client_cert,
                'ssl.key.location': client_key,
            })
        return result
