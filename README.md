checksite
=========

Check the status of a web site and feed status updates into a Kafka instance. Consume those status updates and write metrics to a PostgreSQL database.

Building
--------

To build docker image:

  docker-compose build


Testing
-------

To run the tests:

  touch config.env
  docker-compose run --rm producer ./test.sh

`config.env` needs to exist for docker-compose. The unit tests don't rely on external configuration at all.


Running
-------

First, create the config file (a set of environment variables acceptable to docker's `--env-file` option):

  cp config.env.in config.env

Prerequisites:

* PostgreSQL with known URL. For example, I created a PostgreSQL instance in Aiven and configured checksite with

    CK_POSTGRESQL_URL=postgres://avnadmin:<pw>@<host>.aivencloud.com:12359/defaultdb

in `config.env`. Connectivity is enough: checksite will create the required tables on its first run.

* Kafka with known bootstrap server and SSL credentials in the current directory. For example, I created a Kafka instance in Aiven; downloaded `service.key`, `service.cert`, and `ca.pem` to my local dir; and configured checksite with

    CK_KAFKA_SERVERS=<host>.aivencloud.com:12361
    CK_KAFKA_SSL='ca.pem service.cert service.key'

in `config.env`. Connectivity is enough: checksite will create the required topic on its first run.

That done, you can run the producer and consumer concurrently:

  docker-compose up
