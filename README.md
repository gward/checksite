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

  docker-compose run --rm producer ./test.sh
