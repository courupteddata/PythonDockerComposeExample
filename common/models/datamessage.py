import gzip
from datetime import datetime
import pydantic


class DataMessage(pydantic.BaseModel):
    content: str
    creation_datetime: datetime

    def serialize(self) -> bytes:
        return gzip.compress(self.model_dump_json().encode())

    @classmethod
    def deserialize(cls, payload: bytes) -> "DataMessage":
        return cls.model_validate_json(gzip.decompress(payload))
