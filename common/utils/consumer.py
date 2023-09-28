import threading
import signal
from common.utils import logger
from concurrent.futures import ThreadPoolExecutor, Future

import pika
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

from typing import Callable

from common.models.datamessage import DataMessage

LOGGER = logger.get_logger(__name__)


class Consumer(threading.Thread):
    def __init__(self, amqp_url: str, queue_names: list[str], on_message: Callable[[DataMessage], bool],
                 durable: bool = True, exchange: str = "test"):
        super().__init__()
        self._amqp_url = amqp_url
        self._queue_names = queue_names
        self._on_message = on_message
        self._durable = durable
        self._exchange = exchange

        parameters = pika.URLParameters(amqp_url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count=1, global_qos=True)

        self._setup()

        signal.signal(signal.SIGINT, self._signal_cleanup)
        signal.signal(signal.SIGTERM, self._signal_cleanup)
        signal.signal(signal.SIGHUP, self._signal_cleanup)

    def _signal_cleanup(self, signum: int, frame):
        LOGGER.info(f"Received signal {signum}")
        if self._connection.is_open:
            self._connection.add_callback_threadsafe(lambda: self._connection.close())

    def _setup(self):
        self._channel.exchange_declare(self._exchange, durable=self._durable, exchange_type=ExchangeType.direct)
        for name in self._queue_names:
            self._channel.queue_declare(queue=name, durable=self._durable)
            self._channel.queue_bind(queue=name, exchange=self._exchange)
            self._channel.basic_consume(queue=name, on_message_callback=self._internal_on_message)

    def _internal_on_message(self, channel: BlockingChannel, method_frame: spec.Basic.Deliver,
                             properties: spec.BasicProperties, body: bytes):

        with ThreadPoolExecutor(max_workers=1) as executor:
            future: Future = executor.submit(self._on_message, DataMessage.deserialize(body))
            while future.running():
                self._connection.process_data_events(time_limit=1)
                self._connection.sleep(1)
            try:
                was_successful = future.result(1)
                if was_successful:
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    return
            except:
                LOGGER.exception("Failed to process")
        channel.basic_nack(delivery_tag=method_frame.delivery_tag)

    def _start_consuming(self):
        # This is a blocking call
        self._channel.start_consuming()

    def is_running(self):
        return self.is_alive()

    def run(self) -> None:
        self._start_consuming()

    def stop(self):
        self._channel.stop_consuming()
        if self._connection.is_open:
            self._connection.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
