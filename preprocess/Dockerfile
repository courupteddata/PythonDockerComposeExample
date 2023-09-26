FROM python:3.11-bookworm
# FROM python:3.11-slim Maybe, will save a lot of space?

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "/usr/local/bin/python", "./main.py" ]
