#!/bin/bash
# Test Frodo CLI connection to your ForgeRock tenant
# Usage: FRODO_HOST=... FRODO_USER=... FRODO_PASSWORD=... ./tests/test_frodo_connection.sh

set -euo pipefail

if [ -z "${FRODO_HOST:-}" ] || [ -z "${FRODO_USER:-}" ] || [ -z "${FRODO_PASSWORD:-}" ]; then
  echo "Error: Set FRODO_HOST, FRODO_USER, and FRODO_PASSWORD environment variables"
  exit 1
fi

echo "Testing Frodo CLI connection..."
echo "  Host: $FRODO_HOST"
echo "  User: $FRODO_USER"
echo ""

if frodo journey list > /dev/null 2>&1; then
  JOURNEY_COUNT=$(frodo journey list | wc -l)
  echo "  Journeys: $JOURNEY_COUNT found"
  echo ""
  echo "Connection successful!"
else
  echo "Connection FAILED. Check your credentials and tenant URL."
  exit 1
fi
