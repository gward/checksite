"""consume site status events from Kafka and write them to PostgreSQL"""

import datetime
import logging
import json
import os
from typing import Iterator, Mapping

import confluent_kafka as kafka

from . import config, models, db

UTC = datetime.timezone.utc

logger = logging.getLogger(__name__)


def make_consumer(cfg: config.Config) -> kafka.Consumer:
    return kafka.Consumer({
        'bootstrap.servers': cfg.kafka_servers,
        'group.id': 'checksite',
    })


def get_events(
        cfg: config.Config,
        consumer: kafka.Consumer) -> Iterator[models.SiteStatus]:
    """Read events from Kafka and yield a sequence of SiteStatus objects"""
    consumer.subscribe([cfg.kafka_topic])
    logger.info('Waiting for events from Kafka')
    while True:                 # until signal or exception
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise kafka.KafkaException(msg.error())
        payload = json.loads(msg.value())

        (ts_type, ts_value) = msg.timestamp()
        assert ts_type != kafka.TIMESTAMP_NOT_AVAILABLE, \
            'messages without timestamp are not supported'
        payload['timestamp'] = datetime.datetime.fromtimestamp(
            ts_value / 1000, UTC)
        yield models.SiteStatus(**payload)


def main(environ: Mapping[str, str]):
    logging.basicConfig(
        format='[%(asctime)s %(levelname)-1.1s %(name)s] %(message)s',
        level=logging.DEBUG)
    cfg = config.Config(environ)

    status_db = db.StatusDB(cfg.postgresql_url)
    status_db.check_schema()

    consumer = make_consumer(cfg)
    try:
        for status in get_events(cfg, consumer):
            logger.info('%r', status)
            status_db.write_status(status)
            status_db.commit()
    finally:
        consumer.close()


if __name__ == '__main__':
    main(os.environ)
