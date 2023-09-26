# Sample file that takes in a file on a bind volume and adds it to the queue
# Direct routing
import base64
import gzip
import os
import time
import pathlib
import json
import pika
from pika.exchange_type import ExchangeType

ROUTING_KEY = "transfer.in"
DIRECTORY_IN = "DIRECTORY_IN"
DIRECTORY_OUT = "DIRECTORY_OUT"
AMQP_URL = "AMQP_URL"


def main():
    directory_in = pathlib.Path(os.environ[DIRECTORY_IN])
    directory_out = pathlib.Path(os.environ[DIRECTORY_OUT])

    parameters = pika.URLParameters(os.environ[AMQP_URL])
    connection = pika.BlockingConnection(parameters)
    main_channel = connection.channel()
    main_channel.exchange_declare("default", exchange_type=ExchangeType.direct)

    while True:
        # Sleep not really needed just don't want crazy IO
        time.sleep(1)

        for item in directory_in.iterdir():
            body = json.dumps({
                "content": base64.b64encode(gzip.compress(item.read_bytes())).decode(),
                "file_creation_timestamp": item.stat().st_ctime
            }).encode()
            test = gzip.compress(item.read_bytes())
            test2 = base64.b64encode(test)
            test2.decode()
            main_channel.basic_publish(
                exchange='default',
                routing_key=ROUTING_KEY,
                body=body,
                properties=pika.BasicProperties(content_type='application/json'))

if __name__ == '__main__':
    main()
