#!/usr/bin/env bash
# ab-version.sh — bump the prototype version (SemVer), append changelog, commit.
# Usage: ab-version.sh <major|minor|patch> [--pre <suffix>] [--message "note"]
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=ab-common.sh
source "$SCRIPT_DIR/ab-common.sh"

[[ $# -ge 1 ]] || die "usage: ab-version.sh <major|minor|patch> [--pre <suffix>] [--message \"note\"]"
BUMP=$1; shift
PRE=""; MSG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pre) PRE=$2; shift 2;;
    --message) MSG=$2; shift 2;;
    *) die "unknown argument: $1";;
  esac
done

require_git_repo
require_clean_tree
load_project

if [[ -n $PRE ]]; then
  next_version "$BUMP" --pre "$PRE"
else
  next_version "$BUMP"
fi

log_info "current latest tag: $(latest_version_tag || echo none)"
log_info "next version:       ${AB_FULL_VERSION}"

MSG=${MSG:-"Release ${AB_FULL_VERSION}"}
append_changelog "$AB_FULL_VERSION" "$MSG"

# release notes file for the next release
mkdir -p handover/release-notes
if [[ ! -f "handover/release-notes/v${AB_FULL_VERSION}.md" ]]; then
  cat > "handover/release-notes/v${AB_FULL_VERSION}.md" <<EOF
# Release Notes — ${AB_PROJECT_NAME} v${AB_FULL_VERSION}

**Tag:** \`ab-prototype-v${AB_FULL_VERSION}\` (created by ab-release.sh)

## Summary
${MSG}

## What's new
- (fill in before release)

## Known limitations (prototype scope)
- (fill in)
EOF
fi

git add handover/CHANGELOG.md "handover/release-notes/v${AB_FULL_VERSION}.md"
git commit -q -m "chore: bump to v${AB_FULL_VERSION} — ${MSG}"
log_ok "committed bump to v${AB_FULL_VERSION} (commit $(git rev-parse --short HEAD))"
log_ok "next: ab-gates.sh to check gates, then ab-release.sh to tag & package"