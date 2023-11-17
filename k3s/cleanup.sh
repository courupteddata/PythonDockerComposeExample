#!/bin/bash

# Cleanup
docker compose down
# rm -f images/airgap-images.tar
rm -f server-id
docker volume rm k3s_k3s-server