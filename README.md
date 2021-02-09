checksite
=========

Check the status of a web site and feed status updates into a Kafka instance. Consume those status updates and write metrics to a PostgreSQL database.

Developed and tested on Ubuntu 20.10 with:

  * Python 3.8 and 3.9
  * Kafka 2.7 running locally
  * Kafka 2.7 running in Aiven cloud
  * PostgreSQL 12.5 running in Aiven cloud
  * docker 19.03 and 20.10
  * docker-compose 1.27 and 1.28


Build
-----

To build the docker image:

    touch config.env
    docker-compose build

(`config.env` just needs to exist for docker-compose. Neither the build nor the unit tests rely on external configuration at all.)


Test
----

To run the tests:

    docker-compose run --rm producer ./test.sh


Run
---

Prerequisites:

* Create the config file (a set of environment variables acceptable to docker's `--env-file` option):

      cp config.env.in config.env

  Check that `CK_SITE_URL`, `CK_CHECK_DELAY`, and `CK_CONTENT_REGEX` do what you want. Then carry on with setting up PostgreSQL and Kafka.

* Setup PostgreSQL with known URL. For example, I created a PostgreSQL instance in Aiven and configured checksite with

      CK_POSTGRESQL_URL=postgres://avnadmin:<pw>@<host>.aivencloud.com:12359/defaultdb

  in `config.env`. Connectivity is enough: checksite will create the required tables on its first run.

* Setup Kafka with known bootstrap server and SSL credentials in the current directory. For example, I created a Kafka instance in Aiven; downloaded `service.key`, `service.cert`, and `ca.pem` to my local dir; and configured checksite with

      CK_KAFKA_SERVERS=<host>.aivencloud.com:12361
      CK_KAFKA_SSL='ca.pem service.cert service.key'

  in `config.env`. Connectivity is enough: checksite will create the required topic on its first run.

That done, you can run the producer and consumer concurrently:

    docker-compose up
