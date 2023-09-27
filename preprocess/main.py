import os
from common.utils.consumer import Consumer
from common.models.datamessage import DataMessage

AMQP_URL = "AMQP_URL"
QUEUE_NAME = "transfer.in"


def on_message(data_message: DataMessage):
    print(data_message)
    return True


def main():
    amqp_url = os.environ[AMQP_URL]
    _consumer = Consumer(amqp_url, [QUEUE_NAME], on_message)

    try:
        print("Starting consuming messages")
        _consumer.start_consuming()
    finally:
        _consumer.cleanup()


if __name__ == '__main__':
    main()
