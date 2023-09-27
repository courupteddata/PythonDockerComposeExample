FROM python:3.11-bookworm
# FROM python:3.11-slim Maybe, will save a lot of space?

ENV DIRECTORY_IN="/tmp/in/"
ENV DIRECTORY_OUT="/tmp/out/"

WORKDIR /usr/src/app

COPY external_in_out/requirements.txt ./
COPY common/requirements.txt ./requirements-common.txt
RUN pip install --no-cache-dir -r requirements-common.txt -r requirements.txt  \
    && mkdir $DIRECTORY_IN $DIRECTORY_OUT

COPY common ./common
COPY external_in_out/main.py .

CMD [ "/usr/local/bin/python", "-u", "./main.py" ]
