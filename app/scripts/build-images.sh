#!/usr/bin/env bash
# Build the three app images with podman. Tag defaults to 1.0 (matches k8s/*.yaml).
set -euo pipefail
cd "$(dirname "$0")/.."
TAG="${TAG:-1.0}"
for component in backend frontend sftp; do
  echo "==> Building localhost/shopcart-${component}:${TAG}"
  podman build -t "localhost/shopcart-${component}:${TAG}" -f "${component}/Containerfile" "${component}"
done
