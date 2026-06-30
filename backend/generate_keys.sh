#!/usr/bin/env bash
#
# generate_keys.sh
# Generates the cryptographic material SecureBank needs:
#   - An RSA 2048-bit key pair used to sign/verify JWTs with RS256.
#   - A Fernet symmetric key used to encrypt account balances at rest.
#
# The RSA keys are written to ./keys/. The Fernet key is printed so it can be
# copied into the ENCRYPTION_KEY environment variable. No secret is ever
# hardcoded in the application source.

set -euo pipefail

KEYS_DIR="$(dirname "$0")/keys"
PRIVATE_KEY_PATH="${KEYS_DIR}/private.pem"
PUBLIC_KEY_PATH="${KEYS_DIR}/public.pem"

mkdir -p "${KEYS_DIR}"

echo "==> Generating RSA private key (2048-bit) at ${PRIVATE_KEY_PATH}"
openssl genpkey -algorithm RSA -out "${PRIVATE_KEY_PATH}" -pkeyopt rsa_keygen_bits:2048

echo "==> Extracting RSA public key to ${PUBLIC_KEY_PATH}"
openssl rsa -pubout -in "${PRIVATE_KEY_PATH}" -out "${PUBLIC_KEY_PATH}"

chmod 600 "${PRIVATE_KEY_PATH}"

echo "==> Generating Fernet encryption key"
# Pick an interpreter that has `cryptography` installed. Prefer the project's
# virtualenv, then fall back to whatever Python is on PATH (python3 or python).
if [ -x "$(dirname "$0")/.venv/bin/python" ]; then
  PYTHON="$(dirname "$0")/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "ERROR: no Python interpreter found to generate the Fernet key." >&2
  exit 1
fi

FERNET_KEY="$("${PYTHON}" -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

echo ""
echo "RSA key pair written to ${KEYS_DIR}/"
echo "Add the following line to your .env file:"
echo ""
echo "ENCRYPTION_KEY=${FERNET_KEY}"
echo ""
echo "Done."
