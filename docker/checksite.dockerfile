FROM python:3.9-slim

# just enough to install dependencies
RUN mkdir /src /src/checksite
ADD requirements.txt setup.py /src/
WORKDIR /src

# runtime dependencies
RUN pip install -r requirements.txt

# build/dev dependencies
RUN pip install -e '.[dev]'

# the rest of the code
ADD . /src
