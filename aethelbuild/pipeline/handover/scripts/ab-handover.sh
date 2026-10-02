#!/usr/bin/env bash
# ab-handover.sh — freeze the handover branch and build the client bundle.
# Usage: ab-handover.sh -c <client> [-v <version>] [-o <outdir>]
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=ab-common.sh
source "$SCRIPT_DIR/ab-common.sh"

CLIENT=""; VERSION=""; OUTDIR=${AB_OUT_DIR:-handover/bundles}
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c) CLIENT=$2; shift 2;;
    -v) VERSION=$2; shift 2;;
    -o) OUTDIR=$2; shift 2;;
    *) die "unknown argument: $1";;
  esac
done
[[ -n $CLIENT ]] || die "usage: ab-handover.sh -c <client> [-v <version>] [-o <outdir>]"
# absolute outdir (zip runs from a temp workdir; relative paths would break)
mkdir -p "$OUTDIR"
OUTDIR=$(cd "$OUTDIR" && pwd) || die "cannot resolve outdir $OUTDIR"
# file-safe client slug (display name stays untouched in the manifest)
CLIENT_SLUG=$(printf '%s' "$CLIENT" | tr '[:space:]/\\' '----' | sed 's/-*$//' | tr -cd '[:alnum:]_-')
[[ -n $CLIENT_SLUG ]] || die "client name produced an empty file slug"

require_git_repo
require_clean_tree
load_project

# resolve the release to hand over
if [[ -n $VERSION ]]; then
  validate_version "$VERSION"
else
  VERSION=$(latest_version_tag || true)
  [[ -n $VERSION ]] || die "no release tag found — run ab-release.sh first"
fi
TAG="${AB_TAG_PREFIX}${VERSION}"
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null || die "tag $TAG not found"
# always dereference to the commit (annotated tags are tag objects)
RELEASE_COMMIT=$(git rev-parse "$TAG^{commit}")
RELEASE_SHA=$RELEASE_COMMIT

# freeze handover branch at the release commit (idempotent, guarded)
HB="handover/v${VERSION}"
if git rev-parse -q --verify "refs/heads/$HB" >/dev/null; then
  cur=$(git rev-parse "$HB^{commit}")
  if [[ $cur != "$RELEASE_COMMIT" ]]; then
    die "handover branch $HB exists but points at $cur (expected $RELEASE_COMMIT) — delete the stale branch and retry"
  fi
  log_ok "handover branch $HB already frozen at release commit — reusing"
else
  git branch "$HB" "$RELEASE_COMMIT"
  log_ok "created frozen handover branch $HB @ $RELEASE_COMMIT"
fi
HANDOVER_SHA=$(git rev-parse "$HB^{commit}")

# changelog checksum + release notes
CHANGELOG_HASH=$(git show "$TAG":handover/CHANGELOG.md 2>/dev/null | sha256sum | awk '{print $1}')
NOTES_FILE=$(git show "$TAG":handover/release-notes/v${VERSION}.md 2>/dev/null >/dev/null && echo present || echo absent)
[[ $NOTES_FILE == present ]] || log_warn "release notes handover/release-notes/v${VERSION}.md missing from tag"

# artifact (from tag, deterministic)
mkdir -p "$OUTDIR"
"$SCRIPT_DIR/ab-package.sh" -v "$VERSION" -o "$OUTDIR/artifacts" "$TAG" >/dev/null
ART_NAME=$(ls -1 "$OUTDIR/artifacts"/ab-prototype-*-v${VERSION}-*.tar.gz | tail -1 | xargs basename)
ART_HASH=$(cat "$OUTDIR/artifacts/${ART_NAME%.tar.gz}.tar.gz.sha256")

# assemble bundle -------------------------------------------------------
STAMP=$(stamp_date)
BUNDLE_NAME="ab-handover-${CLIENT_SLUG}-v${VERSION}-${STAMP}"
BUNDLE="$OUTDIR/$BUNDLE_NAME.zip"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/$BUNDLE_NAME/"{SOURCE,ARTIFACT,docs}

# SOURCE: exact handover tree
git archive --format=tar --prefix="$BUNDLE_NAME/SOURCE/" "$HB" | tar -xf - -C "$WORK"
# ARTIFACT
cp "$OUTDIR/artifacts/$ART_NAME" "$OUTDIR/artifacts/$ART_NAME.sha256" "$WORK/$BUNDLE_NAME/ARTIFACT/"
echo "SHA256($ART_NAME) = $ART_HASH" > "$WORK/$BUNDLE_NAME/ARTIFACT/SHA256SUMS"
# docs from handover tree (skip dirs absent from the release tree)
for d in docs deploy handover/release-notes; do
  if git ls-tree -d --name-only "$HB" "$d" | grep -q .; then
    git archive --format=tar "$HB" "$d" | tar -xf - -C "$WORK/$BUNDLE_NAME"
  fi
done
# release notes copy at bundle root
if git show "$TAG":handover/release-notes/v${VERSION}.md >/dev/null 2>&1; then
  git show "$TAG":handover/release-notes/v${VERSION}.md > "$WORK/$BUNDLE_NAME/RELEASE_NOTES.md"
fi

# gate checklist verbatim
GATES_SHA256=$(git show "$TAG":quality-gates/gate-checklist.yaml 2>/dev/null | sha256sum | awk '{print $1}')

# ---- manifest --------------------------------------------------------------
REPO_URL=$(git remote get-url origin 2>/dev/null || echo "(repolink pending)")
BUILDER=$(builder_name)
NOW=$(utc_now)
GATE_YAML=$(git show "$TAG":quality-gates/gate-checklist.yaml 2>/dev/null || echo "# gate checklist missing from tag")

manifest="$WORK/$BUNDLE_NAME/MANIFEST.md"
sed -e "s/{{CLIENT}}/$CLIENT/g" \
    -e "s/{{PROTOTYPE_NAME}}/$AB_PROJECT_NAME/g" \
    -e "s/{{VERSION}}/$VERSION/g" \
    -e "s|{{REPO_URL}}|$REPO_URL|g" \
    -e "s/{{RELEASE_SHA}}/$RELEASE_SHA/g" \
    -e "s/{{HANDOVER_SHA}}/$HANDOVER_SHA/g" \
    -e "s/{{CHANGELOG_SHA256}}/$CHANGELOG_HASH/g" \
    -e "s/{{ARTIFACT_NAME}}/$ART_NAME/g" \
    -e "s/{{ARTIFACT_SHA256}}/$ART_HASH/g" \
    -e "s|{{BUNDLE_NAME}}|$BUNDLE_NAME|g" \
    -e "s/{{DATE_UTC}}/$NOW/g" \
    -e "s/{{BUILDER}}/$BUILDER/g" \
    "$SCRIPT_DIR/../templates/HANDOVER_MANIFEST.md.tpl" > "$manifest"

# substitute the {{GATE_YAML}} placeholder line with the verbatim checklist
awk -v yaml="$GATE_YAML" '{ if ($0 ~ /^{{GATE_YAML}}$/) { print yaml } else { print } }' \
  "$manifest" > "$manifest.tmp" && mv "$manifest.tmp" "$manifest"

# ---- zip + sidecar (single pass; the .sha256 sidecar is the bundle's own
# authoritative checksum — the manifest references it by name) ---------------
rm -f "$BUNDLE" "$BUNDLE.sha256"
( cd "$WORK" && zip -qr "$BUNDLE" "$BUNDLE_NAME" )
sha256sum "$BUNDLE" | awk '{print $1}' > "$BUNDLE.sha256"
BUNDLE_HASH=$(cat "$BUNDLE.sha256")

log_ok "handover bundle:"
log_ok "  bundle    $BUNDLE"
log_ok "  sha256    $(cat "$BUNDLE.sha256")"
log_ok "  tag       $TAG ($RELEASE_SHA)"
log_ok "  handover  $HB ($HANDOVER_SHA)"
log_ok "verify with: ab-verify.sh $BUNDLE_NAME.zip"