#!/usr/bin/env bash
# Copy the locally built images into the kind cluster's node.
# kind cannot read podman's image store directly, so each image is saved to a
# tar archive and loaded from there. Also loads mongo so the cluster needs no pulls.
set -euo pipefail
CLUSTER="${CLUSTER:-shopcart}"
TAG="${TAG:-1.0}"
export KIND_EXPERIMENTAL_PROVIDER=podman
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

podman image exists docker.io/library/mongo:7.0 || podman pull docker.io/library/mongo:7.0
for image in localhost/shopcart-backend:${TAG} localhost/shopcart-frontend:${TAG} \
             localhost/shopcart-sftp:${TAG} docker.io/library/mongo:7.0; do
  echo "==> Loading ${image} into kind cluster '${CLUSTER}'"
  archive="${TMP}/$(echo "$image" | tr '/:' '__').tar"
  podman save -o "$archive" "$image"
  kind load image-archive "$archive" --name "$CLUSTER"
done
