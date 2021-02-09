"""check site status and send events to Kafka"""

import dataclasses
import json
import logging
import os
import socket
import sys
import time
from typing import Optional, Mapping

import confluent_kafka as kafka
from confluent_kafka import admin
import requests

from . import config, models

logger = logging.getLogger(__name__)


def check_site(cfg: config.Config) -> models.SiteStatus:
    # Using requests without an explicit Session always opens a new TCP
    # connection. Normally, I would avoid this behaviour! But for checking
    # availability, it seems worthwhile to ensure that a new connection
    # works. Also, this is likely to run in a new process every time (eg.
    # triggered by cron), so it's not worth the bother of creating a
    # Session.
    logger.debug('Checking site: GET %s', cfg.site_url)
    t0 = time.time()
    error: Optional[str] = None
    try:
        resp = requests.get(cfg.site_url)
    except requests.exceptions.RequestException as err:
        error = str(err)
        status = None
    else:
        status = resp.status_code

    t1 = time.time()
    body_prefix = content_match = None
    if status == 200:
        if match := cfg.content_regex.search(resp.text):
            content_match = match.group()
    elif status is not None:
        body_prefix = resp.text[0:500]

    return models.SiteStatus(
        url=cfg.site_url,
        error=error,
        status=status,
        elapsed=round((t1 - t0) * 1000),
        body_prefix=body_prefix,
        content_match=content_match,
    )


def create_topic(cfg: config.Config):
    """Ensure that the required Kafka topic exists."""
    # based on code in https://github.com/confluentinc/confluent-kafka-python
    client = admin.AdminClient(cfg.get_kafka_config())
    topic = admin.NewTopic(
        cfg.kafka_topic, num_partitions=3, replication_factor=1)
    topic_map = client.create_topics([topic])

    for (topic, future) in topic_map.items():
        try:
            future.result()
            logger.info('Topic %s created', topic)
        except Exception as err:
            if err.args[0].code() != kafka.KafkaError.TOPIC_ALREADY_EXISTS:
                raise
            logger.debug('Topic %s already exists', topic)


def make_producer(cfg: config.Config) -> kafka.Producer:
    return kafka.Producer({
        **cfg.get_kafka_config(),
        'client.id': socket.gethostname(),
    })


def send_status(
        cfg: config.Config,
        producer: kafka.Producer,
        status: models.SiteStatus):
    """Send site status event to Kafka.
    """
    logger.debug('Sending status %r to Kafka', status)
    producer.produce(
        cfg.kafka_topic,
        key=status.url,
        value=json.dumps(dataclasses.asdict(status)),
    )


def main(environ: Mapping[str, str]) -> int:
    logging.basicConfig(
        format='[%(asctime)s %(levelname)-1.1s %(name)s] %(message)s',
        level=logging.DEBUG)
    cfg = config.Config(environ)

    create_topic(cfg)

    producer = make_producer(cfg)

    # Detecting failure to send an event to Kafka is tricky. Because the
    # client library aggressively retries, failures tend to disappear
    # inside the library. That's great if there's a transient problem
    # reaching Kafka that will be resolved in a few seconds.
    #
    # But if kafka_servers is misconfigured, or the server in question is
    # permanently down, there's not much we can do. If the server is
    # down/unreachable at startup, create_topic() retries for a while and
    # then fails. This code never has a chance to run. If the producer
    # starts up OK and then Kafka goes away, it's _possible_ to detect that
    # with an elaborate dance involving callbacks and producer.flush(). Not
    # clear it's worth the trouble; Kafka _is_ supposed to be highly
    # available, after all.
    #
    # So I'm just blithely assuming that sending events eventually succeeds.

    while True:
        status = check_site(cfg)
        send_status(cfg, producer, status)
        time.sleep(cfg.check_delay)


if __name__ == '__main__':
    sys.exit(main(os.environ))
