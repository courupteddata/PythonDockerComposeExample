#!/bin/bash

# Cleanup
K3S_TOKEN=189652679513755 docker compose down
# rm -f images/airgap-images.tar
docker volume rm k3s_k3s-server k3s_k3s-agent