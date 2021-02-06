FROM python:3.9-slim

# runtime dependencies
RUN pip install \
  confluent-kafka \
  requests

# build/dev dependencies
RUN pip install \
  flake8 \
  mypy

# application code (will be overridden with a mount for development)
RUN mkdir /src
ADD . /src
WORKDIR /src
