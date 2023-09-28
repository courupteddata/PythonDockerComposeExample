import signal
import threading
from typing import Callable

import pika
from pika.delivery_mode import DeliveryMode
from pika.exchange_type import ExchangeType
from pika.exceptions import UnroutableError
from common.models.datamessage import DataMessage
from common.utils import logger

LOGGER = logger.get_logger(__name__)


class Producer(threading.Thread):

    def __init__(self, amqp_url: str, queue_names: list[str], durable: bool = True, exchange: str = "test"):
        super().__init__()
        self.daemon = True
        self._is_running = True

        self._amqp_url = amqp_url
        self._queue_names = queue_names
        self._durable = durable
        self._exchange = exchange

        parameters = pika.URLParameters(amqp_url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        self._setup()

        signal.signal(signal.SIGINT, self._signal_cleanup)
        signal.signal(signal.SIGTERM, self._signal_cleanup)
        signal.signal(signal.SIGHUP, self._signal_cleanup)

    def _signal_cleanup(self, signum: int, frame):
        LOGGER.info(f"Received signal {signum}")
        self._is_running = False

    def _setup(self):
        self._channel.exchange_declare(self._exchange, durable=self._durable, exchange_type=ExchangeType.direct)
        for name in self._queue_names:
            self._channel.queue_declare(queue=name, durable=self._durable)

        # Turn on delivery confirmations
        self._channel.confirm_delivery()

    def publish(self, data_message: DataMessage, queue_name: str, publish_response: Callable[[bool], None]):
        self._connection.add_callback_threadsafe(lambda: self._publish(data_message, queue_name, publish_response))

    def _publish(self, data_message: DataMessage, queue_name: str, publish_response: Callable[[bool], None]):
        try:
            self._channel.basic_publish(exchange=self._exchange,
                                        routing_key=queue_name,
                                        body=data_message.serialize(),
                                        properties=pika.BasicProperties(content_type="binary",
                                                                        expiration="86400000", # Expiration 24 hours in milliseconds
                                                                        delivery_mode=DeliveryMode.Persistent.value))
            publish_response(True)
        except UnroutableError:
            LOGGER.error('Message could not be confirmed')
            publish_response(True)

    def run(self):
        while self._is_running:
            try:
                self._connection.process_data_events(time_limit=1)
            except Exception as e:
                self._is_running = False
                LOGGER.warning(f"Closing producer: {e}")

    def is_running(self):
        return self._is_running

    def stop(self):
        self._is_running = False

        # Wait until all the data events have been processed
        self._connection.process_data_events(time_limit=1)
        if self._connection.is_open:
            self._connection.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        try:
            self.join(timeout=1)
        except TimeoutError:
            pass
