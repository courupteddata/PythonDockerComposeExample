FROM python:3.11-bookworm
# FROM python:3.11-slim Maybe, will save a lot of space?

WORKDIR /usr/src/app

COPY process/requirements.txt ./
COPY common/requirements.txt ./requirements-common.txt
RUN pip install --no-cache-dir -r requirements-common.txt -r requirements.txt

COPY common ./common
COPY process/main.py .

CMD [ "/usr/local/bin/python", "-u", "./main.py" ]
