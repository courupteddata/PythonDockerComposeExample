"""Basic message consumer example"""
import functools
import os
import pika
from pika.exchange_type import ExchangeType

AMQP_URL = "AMQP_URL"
ROUTING_KEY = "transfer.in"


def on_message(chan, method_frame, header_frame, body, userdata=None):
    """Called when a message is received. Log message and ack it."""
    print('Delivery properties: %s, message metadata: %s', method_frame, header_frame)
    print('Userdata: %s, message body: %s', userdata, body)
    chan.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
    """Main method."""
    parameters = pika.URLParameters(os.environ[AMQP_URL])
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(
        exchange='default',
        exchange_type=ExchangeType.direct,
        passive=False,
        durable=True,
        auto_delete=False)
    channel.queue_bind(queue='standard', exchange='default', routing_key=ROUTING_KEY)
    channel.basic_qos(prefetch_count=1)

    on_message_callback = functools.partial(
        on_message, userdata='on_message_userdata')
    channel.basic_consume('standard', on_message_callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    main()
