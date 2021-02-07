checksite
=========

Check the status of a web site and feed status updates into a Kafka instance. Consume those status updates and write metrics to a PostgreSQL database.

Building
--------

To build docker images:

  docker build --tag checksite:latest -f docker/checksite.dockerfile .


Testing
-------

To run the tests:

  docker run --rm -v $PWD:/src checksite:latest ./test.sh
