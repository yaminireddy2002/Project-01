#!/usr/bin/env bash

set -euo pipefail

SERVICE="nginx.service"
HEALTH_URL="http://localhost"

echo "Checking if service exists..."

if ! systemctl cat "$SERVICE" >/dev/null 2>&1; then
echo "ERROR: $SERVICE not found."
exit 1
fi

echo "Capturing current status..."
systemctl status "$SERVICE" --no-pager > nginx-status-before.txt

echo "Restarting service..."
sudo systemctl restart "$SERVICE"

sleep 3

echo "Verifying service status..."
if ! systemctl is-active --quiet "$SERVICE"; then
echo "FAIL: Service is not active."
exit 2
fi

echo "Verifying web response..."
if curl -fsS "$HEALTH_URL" >/dev/null; then
echo "SUCCESS: nginx is healthy."
exit 0
else
echo "FAIL: Health check failed."
exit 3
fi
