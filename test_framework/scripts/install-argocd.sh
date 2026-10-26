#!/usr/bin/env bash
# Install ArgoCD in the current kubectl context and register the ApplicationSet that
# runs the Robot Framework suite in the shopcart namespace for every open pull request.
set -euo pipefail
cd "$(dirname "$0")/.."
ARGOCD_VERSION="${ARGOCD_VERSION:-v3.5.6}"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
# Server-side apply: the ArgoCD CRDs are too large for client-side apply annotations.
kubectl apply -n argocd --server-side --force-conflicts \
  -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"
for d in argocd-server argocd-repo-server argocd-applicationset-controller; do
  kubectl -n argocd rollout status "deployment/$d" --timeout=300s
done
kubectl -n argocd rollout status statefulset/argocd-application-controller --timeout=300s
kubectl apply -f argocd/applicationset.yaml
echo
echo "ArgoCD UI: kubectl -n argocd port-forward svc/argocd-server 8443:443  ->  https://localhost:8443"
echo "Login: admin / \$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"
