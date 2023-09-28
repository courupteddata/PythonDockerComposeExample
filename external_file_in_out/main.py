import os
import pathlib
from datetime import datetime

from common.interface.step import Step
from common.models.datamessage import DataMessage
from common.utils import logger

LOGGER = logger.get_logger(__name__)

QUEUE_OUT_NAME = "file.external.in"
DIRECTORY_IN = "DIRECTORY_IN"
DIRECTORY_OUT = "DIRECTORY_OUT"
AMQP_URL = "AMQP_URL"


class PreProcess(Step):
    def __init__(self, amqp_url: str, input_directories: list[pathlib.Path]):
        consume_queues = []
        produce_queues = [QUEUE_OUT_NAME]
        super().__init__(amqp_url, consume_queues, produce_queues)

        self._input_directories = input_directories
        self._existing_files = {}
        for input_dir in self._input_directories:
            self._existing_files[str(input_dir)] = set()

    def work(self):
        for directory in self._input_directories:
            found_files = set()
            existing_files = self._existing_files[str(directory)]

            for item in directory.iterdir():
                if item.name.startswith("."):
                    continue

                found_files.add(item.name)
                if item.name in existing_files:
                    continue
                self.logger.info(f"Found item: {item}")
                message = DataMessage(content=item.read_text(),
                                      creation_datetime=datetime.fromtimestamp(item.stat().st_ctime))
                if self.blocking_publish(message, QUEUE_OUT_NAME):
                    item.unlink()
                else:
                    found_files.remove(item.name)
            self._existing_files[str(directory)] = found_files

    def handle_message(self, data_message: DataMessage, queue_name: str) -> bool:
        # Not really necessary
        return True


def main():
    amqp_url = os.environ[AMQP_URL]
    input_directories = [pathlib.Path(item) for item in os.environ[DIRECTORY_IN].split(",")]
    PreProcess(amqp_url, input_directories).run()


if __name__ == "__main__":
    main()
