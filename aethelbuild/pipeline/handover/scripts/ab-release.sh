#!/usr/bin/env bash
# ab-release.sh — cut a formal AethelBuild release.
# Gates must pass; working tree must be clean; then: version bump → release
# branch → annotated tag → package → summary.
# Usage: ab-release.sh <major|minor|patch> [--pre <suffix>] [--message "note"]
#        ab-release.sh --version X.Y.Z      (release an already-bumped version)
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=ab-common.sh
source "$SCRIPT_DIR/ab-common.sh"

require_git_repo
require_clean_tree
load_project

VERSION="" ; BUMP=""; PRE=""; MSG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION=$2; shift 2;;
    --pre) PRE=$2; shift 2;;
    --message) MSG=$2; shift 2;;
    major|minor|patch) BUMP=$1; shift;;
    *) die "unknown argument: $1";;
  esac
done

if [[ -n $VERSION ]]; then
  validate_version "$VERSION"
  # release of an already-committed version: ensure it isn't tagged already
  git rev-parse -q --verify "refs/tags/${AB_TAG_PREFIX}${VERSION}" >/dev/null \
    && die "tag ab-prototype-v$VERSION already exists"
else
  [[ -n $BUMP ]] || die "usage: ab-release.sh <major|minor|patch> [--version X.Y.Z]"
  if [[ -z $(latest_version_tag || true) ]]; then
    # first release: tag the scaffold baseline v0.1.0 (changelog already has it)
    VERSION="0.1.0"; [[ -z $PRE ]] || VERSION="0.1.0-$PRE"
    log_info "first release — tagging scaffold baseline v$VERSION"
  else
    if [[ -n $PRE ]]; then next_version "$BUMP" --pre "$PRE"; else next_version "$BUMP"; fi
    VERSION=$AB_FULL_VERSION
  fi
fi

log_info "release: ${AB_PROJECT_NAME} v${VERSION}"

# 1) gates
"$SCRIPT_DIR/ab-gates.sh"

# 2) ensure release notes describe this version
NOTES="handover/release-notes/v${VERSION}.md"
mkdir -p handover/release-notes
if [[ ! -f $NOTES ]]; then
  cat > "$NOTES" <<EOF
# Release Notes — ${AB_PROJECT_NAME} v${VERSION}

**Tag:** \`ab-prototype-v${VERSION}\`

## Summary
${MSG:-Release ${VERSION}}
EOF
  git add "$NOTES"
  git commit -q -m "docs: release notes v${VERSION}"
fi

# 3) package FIRST from HEAD (secret scan + artifact build). If this fails,
#    no tag is created — a leaked secret can never be enshrined in a release
#    tag. HEAD == the release commit (tag is created right after).
ART_DIR=handover/releases
"$SCRIPT_DIR/ab-package.sh" -v "$VERSION" -o "$ART_DIR"

# 4) create/confirm release branch at HEAD
if ! git show-ref -q "refs/heads/release/v${VERSION}"; then
  git branch "release/v${VERSION}"
  log_ok "created branch release/v${VERSION}"
fi

# 5) annotated tag on current HEAD (the commit that carries changelog+notes)
TAG="${AB_TAG_PREFIX}${VERSION}"
if ! git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  git tag -a "$TAG" -m "AethelBuild ${AB_PROJECT_NAME} v${VERSION} — ${MSG:-release}"
  log_ok "created annotated tag $TAG"
else
  log_warn "tag $TAG already exists — reusing"
fi

TAG_SHA=$(git rev-parse "$TAG")
log_ok "release complete:"
log_ok "  version    v${VERSION}"
log_ok "  tag        $TAG ($(git rev-parse --short "$TAG"))"
log_ok "  release sha ${TAG_SHA}"
log_ok "  artifact   $(ls -1 "$ART_DIR"/ab-prototype-*-v${VERSION}-*.tar.gz 2>/dev/null | tail -1 || echo none)"
log_ok "next: ab-handover.sh -c <client> -v ${VERSION}"