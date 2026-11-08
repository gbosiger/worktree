#!/usr/bin/env bash
# Requires separately approved publication and already validated/smoked assets.
set -euo pipefail
tag=${1:?version tag required}
assets=${2:?asset directory required}
[[ $tag =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
version=${tag#v}
notes="$assets/notes.md"
test -s "$notes"
test -s "$assets/worktree-tickets-$version.tar.gz"
test -s "$assets/worktree-tickets-$version.zip"
if ! gh release view "$tag" > /dev/null; then
  gh release create "$tag" --verify-tag --draft --title "$version" --notes-file "$notes"
fi
# A failed upload leaves a new release in draft. Reruns replace only our two assets.
gh release upload "$tag" "$assets/worktree-tickets-$version.tar.gz" \
  "$assets/worktree-tickets-$version.zip" --clobber
gh release edit "$tag" --verify-tag --title "$version" --notes-file "$notes" \
  --draft=false --prerelease=false --latest
