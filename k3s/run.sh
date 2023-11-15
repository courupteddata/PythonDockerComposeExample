#!/bin/bash

# Pull all "airgap" images and save them to a tar
SAVE_STRING=""
while read image; do
  docker pull ${image}
  SAVE_STRING+=" ${image}"
done <airgap-images.txt

mkdir -m 777 images
docker save -o images/airgap-images.tar ${SAVE_STRING}

echo
/etc/machine-id

# Start
K3S_TOKEN=189652679513755 docker compose up