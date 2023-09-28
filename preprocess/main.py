import os
from common.utils.consumer import Consumer
from common.models.datamessage import DataMessage
from common.utils import logger

LOGGER = logger.get_logger(__name__)

AMQP_URL = "AMQP_URL"
QUEUE_NAME = "transfer.in"


def on_message(data_message: DataMessage):
    LOGGER.info(data_message)
    return True


def main():
    amqp_url = os.environ[AMQP_URL]

    with Consumer(amqp_url, [QUEUE_NAME], on_message) as _consumer:
        while _consumer.is_running():
            pass


if __name__ == '__main__':
    main()
