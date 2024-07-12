#!/usr/bin/env bash

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

image="${args[1]}"
pyver=default
# check for explicit python version like 8.3@3.8
declare -a splitversion
IFS='@' read -ra splitversion <<< "$image"

if [ "${#splitversion[@]}" -gt 1 ]; then
    image="${splitversion[0]}"
    pyver="${splitversion[1]}"
fi

if [ "${#args[@]}" -gt 2 ]; then
    target="shippable/posix/group${args[2]}/"
else
    target="shippable/posix/"
fi

# shellcheck disable=SC2086
ansible-test integration --color -v --retry-on-error "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"} \
    --docker "${image}" --python "${pyver}"
