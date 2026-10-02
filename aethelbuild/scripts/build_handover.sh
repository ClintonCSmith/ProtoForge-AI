#!/usr/bin/env bash
# build_handover.sh — produce a signed/versioned handover bundle for a release.
# Usage: build_handover.sh [-v <version>] [-o <outdir>]   (run inside the
# delivery repo; -v defaults to the latest v* git tag)
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AETHELBULD_ROOT=$(dirname "$HERE")
TEMPLATE="$AETHELBULD_ROOT/templates/HANDOVER.md.tpl"

VERSION=""; OUTDIR=${AB_OUT_DIR:-releases/bundles}
while [[ $# -gt 0 ]]; do
  case "$1" in
    -v) VERSION=$2; shift 2;; -o) OUTDIR=$2; shift 2;;
    *) echo "unknown: $1" >&2; exit 1;;
  esac
done
# absolute outdir (zip runs from a temp dir; relative paths would break)
mkdir -p "$OUTDIR"
OUTDIR=$(cd "$OUTDIR" && pwd) || { echo "cannot resolve outdir $OUTDIR" >&2; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "run inside the delivery repo" >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "working tree not clean" >&2; exit 1; }

# resolve version (default: latest v* tag)
if [[ -z $VERSION ]]; then
  VERSION=$(git tag -l 'v*' | sed 's/^v//' | sort -V | tail -1 || true)
  [[ -n $VERSION ]] || { echo "no v* tag found — create one (see RELEASING.md)" >&2; exit 1; }
fi
TAG="v$VERSION"
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null || { echo "tag $TAG not found" >&2; exit 1; }
RELEASE_SHA=$(git rev-parse "$TAG^{commit}")

# secret scan (hard stop)
if git grep -InE 'sk_live_|pk_live_|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |OPENSSH |EC |PGP )?PRIVATE KEY-----' "$TAG" -- src tests infra scripts examples 2>/dev/null; then
  echo "SECRET HIT — handover blocked; move credentials to env.example only" >&2; exit 1
fi
echo "secret scan clean"

# artifact
mkdir -p "$OUTDIR"
ART="aethelbuild-${PWD##*/}-v${VERSION}-$(git rev-parse --short=7 "$TAG").tar.gz"
git archive --format=tar --prefix="${PWD##*/}-v${VERSION}/" "$TAG" | gzip -n -c > "$OUTDIR/$ART"
( cd "$OUTDIR" && sha256sum "$ART" > "$ART.sha256" )
ART_HASH=$(awk '{print $1}' "$OUTDIR/$ART.sha256")

# changelog hash
CH_HASH=$(git show "$TAG":CHANGELOG.md | sha256sum | awk '{print $1}')

# assemble bundle
STAMP=$(date -u +%Y%m%d); CLIENT=${PWD##*/}
BUNDLE_NAME="handover-${CLIENT}-v${VERSION}-${STAMP}"
BUNDLE="$OUTDIR/$BUNDLE_NAME.zip"
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/$BUNDLE_NAME/"{SOURCE,ARTIFACT,docs}
git archive --format=tar --prefix="$BUNDLE_NAME/SOURCE/" "$TAG" | tar -xf - -C "$WORK"
cp "$OUTDIR/$ART" "$WORK/$BUNDLE_NAME/ARTIFACT/"
( cd "$WORK/$BUNDLE_NAME/ARTIFACT" && sha256sum "$ART" > SHA256SUMS )
git archive --format=tar "$TAG" docs | tar -xf - -C "$WORK/$BUNDLE_NAME" 2>/dev/null || true

# HANDOVER.md (from template; template is in the kit, not the delivery)
sed -e "s/{{CLIENT_NAME}}/$(sed -n 's/^client: //p' ENGAGEMENT.yaml 2>/dev/null || echo "$CLIENT")/g" \
    -e "s/{{PROTOTYPE}}/$(sed -n 's/^slug: //p' ENGAGEMENT.yaml 2>/dev/null || echo "$CLIENT")/g" \
    -e "s/{{VERSION}}/$VERSION/g" -e "s/{{DATE_UTC}}/$(date -u +%Y-%m-%dT%H:%M:%SZ)/g" \
    -e "s/{{BUILDER}}/${AB_BUILDER:-$(whoami)}/g" \
    -e "s/{{TAG}}/$TAG/g" -e "s/{{RELEASE_SHA}}/$RELEASE_SHA/g" \
    -e "s/{{HANDOVER_BRANCH}}/$TAG/g" -e "s/{{HANDOVER_SHA}}/$RELEASE_SHA/g" \
    -e "s/{{ARTIFACT_NAME}}/$ART/g" -e "s/{{ARTIFACT_SHA256}}/$ART_HASH/g" \
    -e "s/{{CHANGELOG_SHA256}}/$CH_HASH/g" \
    -e "s/{{SUPPORT_DAYS}}/$(sed -n 's/^support_window_days: //p' ENGAGEMENT.yaml 2>/dev/null || echo 30)/g" \
    "$TEMPLATE" > "$WORK/$BUNDLE_NAME/HANDOVER.md"

( cd "$WORK" && zip -qr "$BUNDLE" "$BUNDLE_NAME" )
( cd "$OUTDIR" && sha256sum "$BUNDLE_NAME.zip" > "$BUNDLE_NAME.zip.sha256" )
echo "handover bundle: $BUNDLE ($(awk '{print $1}' "$OUTDIR/$BUNDLE_NAME.zip.sha256"))"
echo "verify: cd releases/bundles && sha256sum -c *.sha256"
