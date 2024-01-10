#!/usr/bin/env bash

set -o pipefail -eux

echo "${PATH/\~/${HOME}}"
echo "${HOME}"
command -v ansible

pip install --upgrade --user pip
pip install --upgrade --user ansible-lint

PATH="${PATH/\~/${HOME}}" ansible-lint \
                                    --exclude changelogs/ \
                                    --profile=production
