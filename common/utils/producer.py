import pika
from pika.delivery_mode import DeliveryMode
from pika.exchange_type import ExchangeType
from pika.exceptions import UnroutableError
from common.models.datamessage import DataMessage


class Producer:
    DEFAULT_EXCHANGE = "test"

    def __init__(self, amqp_url: str, queue_names: list[str], durable: bool = True):
        self._amqp_url = amqp_url
        self._queue_names = queue_names
        self._durable = durable

        parameters = pika.URLParameters(amqp_url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        self._setup()

    def _setup(self):
        self._channel.exchange_declare(self.DEFAULT_EXCHANGE, durable=self._durable, exchange_type=ExchangeType.direct)
        for name in self._queue_names:
            self._channel.queue_declare(queue=name, durable=self._durable)

        # Turn on delivery confirmations
        self._channel.confirm_delivery()

    def produce(self, data_message: DataMessage, queue_name: str):
        # Raises exception on failure and should cause system to restart
        try:
            self._channel.basic_publish(exchange=self.DEFAULT_EXCHANGE,
                                        routing_key=queue_name,
                                        body=data_message.serialize(),
                                        properties=pika.BasicProperties(content_type="binary",
                                                                        expiration="86400000", # Expiration 24 hours in milliseconds
                                                                        delivery_mode=DeliveryMode.Persistent.value))
            print('Message publish was confirmed')
        except UnroutableError:
            print('Message could not be confirmed')

    def cleanup(self):
        self._channel.close()
        self._connection.close()
