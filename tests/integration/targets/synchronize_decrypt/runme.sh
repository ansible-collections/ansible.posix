#!/usr/bin/env bash

set -eux

ansible-playbook -i "${INVENTORY_PATH}" main.yml -e "output_dir=${OUTPUT_DIR}/synchronize_decrypt" --vault-password-file vault-password "$@"

unset ANSIBLE_VAULT_PASSWORD_FILE ANSIBLE_VAULT_IDENTITY_LIST

ansible-playbook -i "${INVENTORY_PATH}" no_secret.yml -e "output_dir=${OUTPUT_DIR}/synchronize_decrypt" "$@"
