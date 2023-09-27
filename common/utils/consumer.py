import pika
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

from typing import Callable

from common.models.datamessage import DataMessage


class Consumer:
    DEFAULT_EXCHANGE = "test"

    def __init__(self, amqp_url: str, queue_names: list[str],
                 on_message: Callable[[DataMessage], bool],
                 durable: bool = True, ):
        self._amqp_url = amqp_url
        self._queue_names = queue_names
        self._on_message = on_message
        self._durable = durable

        parameters = pika.URLParameters(amqp_url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count=1, global_qos=True)

        self._setup()

    def _setup(self):
        self._channel.exchange_declare(self.DEFAULT_EXCHANGE, durable=self._durable, exchange_type=ExchangeType.direct)
        for name in self._queue_names:
            self._channel.queue_declare(queue=name, durable=self._durable)
            self._channel.basic_consume(name, self._internal_on_message)

    def _internal_on_message(self, channel: BlockingChannel, method_frame: spec.Basic.Deliver,
                             properties: spec.BasicProperties, body: bytes):
        print(channel)
        print(method_frame)
        print(properties)
        if self._on_message(DataMessage.deserialize(body)):
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        else:
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)

    def start_consuming(self):
        # This is a blocking call
        self._channel.start_consuming()

    def cleanup(self):
        self._channel.start_consuming()
        self._channel.close()
        self._connection.close()
