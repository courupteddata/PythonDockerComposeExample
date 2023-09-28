# Sample file that takes in a file on a bind volume and adds it to the queue
# Direct routing
import os
import time
import pathlib
from datetime import datetime

from common.models.datamessage import DataMessage
from common.utils import producer, logger

LOGGER = logger.get_logger(__name__)

QUEUE_NAME = "transfer.in"
DIRECTORY_IN = "DIRECTORY_IN"
DIRECTORY_OUT = "DIRECTORY_OUT"
AMQP_URL = "AMQP_URL"


def main():
    directory_in = pathlib.Path(os.environ[DIRECTORY_IN])
    directory_out = pathlib.Path(os.environ[DIRECTORY_OUT])
    amqp_url = os.environ[AMQP_URL]

    _producer = producer.Producer(amqp_url, [QUEUE_NAME])

    def publish_response(was_success: bool):
        LOGGER.info(f"Published message successfully {was_success}")

    with producer.Producer(amqp_url, [QUEUE_NAME]) as _producer:
        existing_files = set()
        while True:
            # Sleep not really needed just don't want crazy IO
            time.sleep(0.001)
            found_files = set()
            for item in directory_in.iterdir():
                found_files.add(item.name)
                if item.name in existing_files:
                    continue
                LOGGER.info(f"Found item: {item}")
                message = DataMessage(content=item.read_text(),
                                      creation_datetime=datetime.fromtimestamp(item.stat().st_ctime))
                _producer.produce(message, QUEUE_NAME, lambda was_success: (item.unlink() if was_success else None))
            existing_files = found_files

if __name__ == '__main__':
    main()
