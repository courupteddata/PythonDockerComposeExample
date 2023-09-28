# Simple Python Docker Compose Example

## Tech stack
* Python 3.11
* RabbitMQ
* Docker Compose?

## Flow
1. external_in_out - provides some text file
2. preprocess - extracts some information and formats it
3. process - does something
4. postprocess - does some packaging thing
5. external_in_out - take the output and puts it somewhere?

## Running
`docker compose up`

## Forcing clean build
`docker compose up --build --force-recreate --no-deps`

## Getting JSON Schema
```python
import json
from common.models.datamessage import DataMessage
print(json.dumps(DataMessage.model_json_schema()))
```