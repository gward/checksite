import dataclasses
import json
from unittest import mock

import confluent_kafka as kafka
import pytest

from checksite import models, consumer


def test_make_consumer(cfg):
    # Same problem here as with testing make_producer(): confluent_kafka's
    # Consumer type doesn't expose any of its innards, so it's hard to
    # assert that it was constructed correctly.
    cons = consumer.make_consumer(cfg)
    assert isinstance(cons, kafka.Consumer)


def test_get_events(cfg):
    mock_consumer = mock.Mock(autospec=kafka.Consumer)

    expect_status = models.SiteStatus(
        url='http://ding:123/bla',
        elapsed=543,
        error=None,
        status=201,
        content_match='foo',
    )

    # one good message, one error message
    msg1 = mock.Mock(autospec=kafka.Message)
    msg1.error.return_value = None
    msg1.value.return_value = json.dumps(dataclasses.asdict(expect_status))
    msg2 = mock.Mock(autospec=kafka.Message)
    msg2.error.return_value = 'kafka broke'
    mock_consumer.poll.side_effect = [
        msg1,
        msg2,
    ]

    # run the loop!
    events = consumer.get_events(cfg, mock_consumer)
    assert next(events) == expect_status
    with pytest.raises(kafka.KafkaException) as exc_info:
        next(events)
    assert str(exc_info.value) == 'kafka broke'
