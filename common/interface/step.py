import time
from contextlib import nullcontext
from typing import Callable

from common.models.datamessage import DataMessage
from common.utils import logger
from common.utils.consumer import Consumer
from common.utils.producer import Producer

class Step:
    def __init__(self, amqp_url: str, consume_queues: list[str], produce_queues: list[str]):
        self._amqp_url = amqp_url
        self._consume_queues = consume_queues
        self._produce_queues = produce_queues
        self._message_producer = None

        self.logger = logger.get_logger(__name__)

        self._was_successful = False
        self._got_response = False

        if not consume_queues and not produce_queues:
            raise ValueError("Both consume_queues and produce_queues can't be null")

    def run(self):
        with Producer(self._amqp_url, self._produce_queues) if len(self._produce_queues) else nullcontext() as _producer:
            self._message_producer = _producer
            with Consumer(self._amqp_url, self._consume_queues, self.handle_message) if len(self._consume_queues) else nullcontext() as _consumer:
                while (_consumer is None or _consumer.is_running()) and (_producer is None or _producer.is_running()):
                    time.sleep(0.0001)
                    self.work()

    def blocking_publish(self, data_message: DataMessage, queue_name: str) -> bool:
        self._was_successful = False
        self._got_response = False

        def publish_response(was_successful):
            self._was_successful = was_successful
            self._got_response = True

        self._message_producer.publish(data_message, queue_name, publish_response)

        while not self._got_response:
            time.sleep(0.001)

        return self._was_successful

    def publish(self, data_message: DataMessage, queue_name: str, publish_response: Callable[[bool], None]) -> None:
        self._message_producer.publish(data_message, queue_name, publish_response)

    def handle_message(self, data_message: DataMessage, queue_name: str) -> bool:
        if self._consume_queues:
            raise NotImplemented("Needs to be implemented on what to do when consume queues are defined.")
        return True

    def work(self):
        raise NotImplemented("Needs to be implemented, this should be on work item")