import re

from checksite import config


def test_config_happy(cfgdict):
    cfg = config.Config(cfgdict)
    assert cfg.site_url == 'http://localhost/'
    assert isinstance(cfg.content_regex, re.Pattern)
    assert cfg.content_regex.pattern == r'Welcome to \w+'
    assert cfg.kafka_ssl == ''
    assert cfg.get_kafka_config() == {
        'bootstrap.servers': '',
    }


def test_config_kafka_ssl(cfgdict):
    cfgdict['CK_KAFKA_SSL'] = 'ca.pem client.crt client.key'
    cfg = config.Config(cfgdict)
    assert cfg.kafka_ssl == 'ca.pem client.crt client.key'
    assert cfg.get_kafka_config() == {
        'bootstrap.servers': '',
        'security.protocol': 'ssl',
        'ssl.ca.location': 'ca.pem',
        'ssl.certificate.location': 'client.crt',
        'ssl.key.location': 'client.key',
    }
