#!/usr/bin/env bash

set -o pipefail -eux

echo "${PATH/\~/${HOME}}"
echo "${HOME}"

pip install --upgrade --user pip
pip install --upgrade --user ansible-lint
command -v ansible
command -v ansible-lint
ansible-lint --version
#ansible-lint --exclude changelogs/ --profile=production -vv
ansible-lint -vv
