FROM python:3.11-bookworm
# FROM python:3.11-slim Maybe, will save a lot of space?

ENV DIRECTORY_IN="/tmp/in/"
ENV DIRECTORY_OUT="/tmp/out/"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && mkdir $DIRECTORY_IN $DIRECTORY_OUT

COPY . .

CMD [ "/usr/local/bin/python", "./main.py" ]
