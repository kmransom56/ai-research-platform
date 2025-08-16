#!/bin/sh
# This script exports Docker secrets as environment variables
# and then executes the command passed to it.

set -e

echo "==> Exporting secrets..."
for secret in /run/secrets/*; do
  if [ -f "$secret" ]; then
    secret_name=$(basename "$secret")
    secret_value=$(cat "$secret")
    export "$secret_name"="$secret_value"
    echo "    Exported secret: $secret_name"
  fi
done
echo "==> Secrets exported."

# Execute the command passed as arguments to the script
exec "$@"
