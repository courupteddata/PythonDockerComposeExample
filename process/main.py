import os

from common.interface.step import Step
from common.models.datamessage import DataMessage
from common.utils import logger

LOGGER = logger.get_logger(__name__)

AMQP_URL = "AMQP_URL"
GENERAL_QUEUE_IN_NAME = "process.in"

QUEUE_OUT_NAME = ""  # TBD?

JAVA_QUEUE_OUT_NAME = "process.java.out"
JAVA_QUEUE_IN_NAME = "process.java.in"


class Process(Step):
    def __init__(self, amqp_url: str):
        consume_queues = [GENERAL_QUEUE_IN_NAME, JAVA_QUEUE_IN_NAME]
        produce_queues = [JAVA_QUEUE_OUT_NAME]
        super().__init__(amqp_url, consume_queues, produce_queues)

    def work(self):
        # Nothing to do in work, this step is only reactionary
        pass

    def handle_message(self, data_message: DataMessage, queue_name: str) -> bool:
        self.logger.info(f"Process Handle: {data_message}, {queue_name}")
        if queue_name == GENERAL_QUEUE_IN_NAME:
            return self.blocking_publish(data_message, JAVA_QUEUE_OUT_NAME)
        elif queue_name == JAVA_QUEUE_IN_NAME:
            self.logger.info(f"Received from java process: {data_message}, {queue_name}")
        return True


def main():
    amqp_url = os.environ[AMQP_URL]
    Process(amqp_url).run()


if __name__ == '__main__':
    main()
