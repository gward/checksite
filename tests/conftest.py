import pytest

from checksite import config


@pytest.fixture
def cfgdict():
    return {
        'CK_SITE_URL': 'http://localhost/',
        'CK_CHECK_DELAY': '15',
        'CK_CONTENT_REGEX': 'Welcome to \\w+',
        'CK_KAFKA_TOPIC': 'checksite',
        'CK_KAFKA_SERVERS': '',
        'CK_KAFKA_SSL': '',
        'CK_POSTGRESQL_URL': '',
    }


@pytest.fixture
def cfg(cfgdict):
    return config.Config(cfgdict)
