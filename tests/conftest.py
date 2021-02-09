import pytest

from checksite import config


@pytest.fixture
def cfg():
    return config.Config({
        "CK_SITE_URL": "http://localhost/",
        "CK_CONTENT_REGEX": "Welcome to \\w+",
        "CK_KAFKA_TOPIC": "checksite",
        "CK_KAFKA_SERVERS": "",
        "CK_KAFKA_SSL": "",
        "CK_POSTGRESQL_URL": "",
    })
