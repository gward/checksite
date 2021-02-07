from unittest import mock

import requests
import requests.exceptions
import vcr

from checksite import producer


# The happy path: we get an HTTP response, status 200, content matches the
# required regex.
@vcr.use_cassette('tests/cassettes/check_site_happy.yaml')
def test_check_site_happy(cfg):
    content_match = 'Welcome to nginx'
    assert_response(cfg, 200, None, content_match)


# Almost happy: 200 response with unexpected content.
@vcr.use_cassette('tests/cassettes/check_site_nomatch.yaml')
def test_check_site_nomatch(cfg):
    assert_response(cfg, 200, None, None)


# Less happy still: a 404 response
@vcr.use_cassette('tests/cassettes/check_site_404.yaml')
def test_check_site_404(cfg):
    body_prefix = '<html>\n<head><title>404 Not Found</title></head>'
    assert_response(cfg, 404, body_prefix, None)


def assert_response(cfg, status_code, body_prefix, content_match):
    status = producer.check_site(cfg)

    assert status.url == cfg.site_url
    assert status.error is None    # because we got an HTTP response
    assert status.status == status_code
    assert isinstance(status.elapsed, int)
    assert status.elapsed >= 0
    if body_prefix is None:
        assert status.body_prefix is None
    else:
        assert status.body_prefix is not None
        assert status.body_prefix.startswith(body_prefix)
    if content_match is None:
        assert status.content_match is None
    else:
        assert status.content_match == content_match


# Testing network error is the odd one out: VCR.py doesn't support this, so
# we have to mock a bit of requests directly.
@mock.patch('requests.get',
            side_effect=requests.exceptions.ConnectionError('no luck'))
def test_check_site_error(cfg):
    status = producer.check_site(cfg)

    assert status.url == cfg.site_url
    assert status.error == 'no luck'
    assert status.status is None
    assert isinstance(status.elapsed, int)
    assert status.elapsed >= 0
    assert status.body_prefix is None
    assert status.content_match is None
