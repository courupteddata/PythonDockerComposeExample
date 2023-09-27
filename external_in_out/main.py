# Sample file that takes in a file on a bind volume and adds it to the queue
# Direct routing
import os
import time
import pathlib
from datetime import datetime

from common.models.datamessage import DataMessage
from common.utils import producer

QUEUE_NAME = "transfer.in"
DIRECTORY_IN = "DIRECTORY_IN"
DIRECTORY_OUT = "DIRECTORY_OUT"
AMQP_URL = "AMQP_URL"


def main():
    directory_in = pathlib.Path(os.environ[DIRECTORY_IN])
    directory_out = pathlib.Path(os.environ[DIRECTORY_OUT])
    amqp_url = os.environ[AMQP_URL]

    _producer = producer.Producer(amqp_url, [QUEUE_NAME])

    try:
        while True:
            # Sleep not really needed just don't want crazy IO
            time.sleep(1)

            for item in directory_in.iterdir():
                print(item)
                message = DataMessage(content=item.read_text(),
                                      creation_datetime=datetime.fromtimestamp(item.stat().st_ctime))
                _producer.produce(message, QUEUE_NAME)
                item.unlink()
    finally:
        _producer.cleanup()


if __name__ == '__main__':
    main()
