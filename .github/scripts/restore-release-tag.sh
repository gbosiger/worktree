#!/usr/bin/env bash
set -euo pipefail
tag=${1:?version tag required}
[[ $tag =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
# checkout can fetch the event's peeled commit into refs/tags, losing annotation.
# Restore only this local runner ref from origin; never alter the published tag.
# prepare-release.py still verifies annotation, version, and equality with HEAD.
git fetch --force --no-tags origin "refs/tags/$tag:refs/tags/$tag"
