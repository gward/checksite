"""check site status and send events to Kafka"""

import dataclasses
import json
import logging
import os
import socket
import sys
import time
from typing import Optional, Callable, Mapping

import confluent_kafka as kafka
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


def make_producer(cfg: config.Config) -> kafka.Producer:
    return kafka.Producer({
        'bootstrap.servers': cfg.kafka_servers,
        'client.id': socket.gethostname(),
    })


def send_status(
        cfg: config.Config,
        producer: kafka.Producer,
        status: models.SiteStatus,
        callback: Callable):
    """Send site status event to Kafka.
    """
    logger.debug('Sending status %r to Kafka', status)
    producer.produce(
        cfg.kafka_topic,
        key=status.url,
        value=json.dumps(dataclasses.asdict(status)),
        callback=callback,
    )


def main(environ: Mapping[str, str]) -> int:
    logging.basicConfig(
        format='[%(asctime)s %(levelname)-1.1s %(name)s] %(message)s',
        level=logging.DEBUG)
    cfg = config.Config(environ)
    producer = make_producer(cfg)

    # Detecting failure to send an event to Kafka is tricky. Because the
    # client library aggressively retries, failures tend to disappear
    # inside the library. That's great if there's a transient problem
    # reaching Kafka that will be resolved in a few seconds.
    #
    # But if kafka_servers is misconfigured, or the server in question is
    # permanently down, it's a bit harder to figure things out. So I let
    # the library retry for 15 sec and then, if we did not get positive
    # confirmation of delivery, assume failure.

    success = False             # assume kafka_callback() never called

    def kafka_callback(err, msg):
        logger.debug('callback invoked: err=%s msg=%s', err, msg)
        nonlocal success
        success = (err is None)

    status = check_site(cfg)
    send_status(cfg, producer, status, kafka_callback)
    producer.flush(15)          # give up on kafka after 15 s
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main(os.environ))
