#!/bin/bash

# Pull all "airgap" images and save them to a tar
SAVE_STRING=""
while read image; do
  docker pull ${image}
  SAVE_STRING+=" ${image}"
done <airgap-images.txt

mkdir -m 777 images
docker save -o images/airgap-images.tar ${SAVE_STRING}
docker save -o images/local-images.tar pythoncomposeexample-external_in_out rabbitmq:3.12-alpine

AGENT_ID="$(uuid -v 4)"
SERVER_ID="$(uuid -v 4)"

echo "${AGENT_ID//-}" > agent-id
echo "${SERVER_ID//-}" > server-id

# Start
K3S_TOKEN=189652679513755 docker compose up