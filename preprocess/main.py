import os

from common.interface.step import Step
from common.models.datamessage import DataMessage
from common.utils import logger

LOGGER = logger.get_logger(__name__)

AMQP_URL = "AMQP_URL"
QUEUE_IN_NAME = "file.external.in"
QUEUE_OUT_NAME = "process.in"


class PreProcess(Step):
    def __init__(self, amqp_url: str):
        consume_queues = [QUEUE_IN_NAME]
        produce_queues = [QUEUE_OUT_NAME]
        super().__init__(amqp_url, consume_queues, produce_queues)

    def work(self):
        # Nothing to do in work, this step only reactionary
        pass

    def handle_message(self, data_message: DataMessage, queue_name: str) -> bool:
        self.logger.info(f"Preprocess Handle: {data_message}, {queue_name}")
        return self.blocking_publish(data_message, QUEUE_OUT_NAME)


def main():
    amqp_url = os.environ[AMQP_URL]
    PreProcess(amqp_url).run()


if __name__ == '__main__':
    main()
