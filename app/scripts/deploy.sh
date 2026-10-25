#!/usr/bin/env bash
# Deploy (or update) the app in the current kubectl context and wait until it is ready.
set -euo pipefail
cd "$(dirname "$0")/.."
kubectl apply -k k8s
# Restart so pods pick up freshly loaded images that reuse the same tag.
kubectl -n shopcart rollout restart deployment/backend deployment/frontend deployment/sftp
for d in mongo sftp backend frontend; do
  kubectl -n shopcart rollout status "deployment/$d" --timeout=180s
done
kubectl -n shopcart get pods,svc
echo
echo "Web app: http://localhost:8080   (if you used kind/kind-config.yaml)"
echo "Otherwise: kubectl -n shopcart port-forward svc/frontend 8080:80"
