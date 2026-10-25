#!/usr/bin/env bash
# Remove the app from the cluster (add --cluster to delete the whole kind cluster).
set -euo pipefail
kubectl delete namespace shopcart --ignore-not-found
if [[ "${1:-}" == "--cluster" ]]; then
  KIND_EXPERIMENTAL_PROVIDER=podman kind delete cluster --name "${CLUSTER:-shopcart}"
fi
