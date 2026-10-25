#!/usr/bin/env bash
# Upload a catalog CSV to the SFTP server.  Usage: scripts/upload-catalog.sh sample-data/catalog.csv
# Password: catalog123 (see k8s/secrets.yaml)
set -euo pipefail
FILE="${1:?usage: $0 <file.csv>}"
HOST="${SFTP_HOST:-localhost}"
PORT="${SFTP_PORT:-2222}"
# The SFTP host key is regenerated when the pod restarts, so skip known_hosts for this demo server.
sftp -P "$PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  catalog@"$HOST" <<< "put ${FILE} upload/"
