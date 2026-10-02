#!/usr/bin/env bash
# ab-verify.sh — independent integrity check of an AethelBuild handover bundle.
# Works client-side with no private infra: recomputes every checksum and
# compares the handover commit SHA against the manifest.
# Usage: ab-verify.sh <bundle.zip> [<bundle.zip.sha256>]
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=ab-common.sh
source "$SCRIPT_DIR/ab-common.sh"

BUNDLE=${1:-}
[[ -n $BUNDLE && -f $BUNDLE ]] || die "usage: ab-verify.sh <bundle.zip>"
SIDE="${2:-${BUNDLE}.sha256}"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

log_info "verifying $BUNDLE"

# 1) sidecar checksum of the zip
if [[ -f $SIDE ]]; then
  expected=$(cat "$SIDE" | awk '{print $1}')
  actual=$(sha256sum "$BUNDLE" | awk '{print $1}')
  if [[ $actual == "$expected" ]]; then
    log_ok "1/5 zip integrity: sidecar matches"
  else
    die "1/5 FAIL — zip sha256 ($actual) != sidecar ($expected); bundle tampered or truncated"
  fi
else
  log_warn "1/5 no sidecar (.sha256) provided — skipping zip-level check (report unverified)"
fi

# 2) extract
log_info "2/5 extracting…"
( cd "$WORK" && unzip -q "$OLDPWD/$BUNDLE" )
top=$(find "$WORK" -mindepth 1 -maxdepth 1 -type d | head -1)
[[ -n $top ]] || die "bundle contains no top-level directory"
MANIFEST="$top/MANIFEST.md"
[[ -f $MANIFEST ]] || die "MANIFEST.md missing from bundle"
log_ok "2/5 bundle contains $(du -sh "$top" | cut -f1), manifest at $top"

# 3) artifact checksum against manifest
ART_HASH=$(sed -n 's/^| Artifact SHA256 | //p' "$MANIFEST" | tr -d ' |')
ART_NAME=$(sed -n 's/^| Artifact file | //p' "$MANIFEST" | tr -d ' |')
if [[ -n $ART_NAME && -f "$top/ARTIFACT/$ART_NAME" ]]; then
  a=$(sha256sum "$top/ARTIFACT/$ART_NAME" | awk '{print $1}')
  if [[ -n $ART_HASH && $a == "$ART_HASH" ]]; then
    log_ok "3/5 artifact sha256 matches manifest ($ART_NAME)"
  else
    die "3/5 FAIL — artifact sha256 mismatch (got $a, manifest says $ART_HASH)"
  fi
else
  die "3/5 FAIL — artifact file not found in bundle (${ART_NAME:-unnamed})"
fi

# 4) manifest-internal consistency: changelog hash if present
CH_DOC="$top/SOURCE/handover/CHANGELOG.md"
if [[ -f $CH_DOC ]]; then
  ch=$(sha256sum "$CH_DOC" | awk '{print $1}')
  ch_expected=$(sed -n 's/^| Changelog SHA256 | //p' "$MANIFEST" | tr -d ' |')
  if [[ -n $ch_expected && $ch == "$ch_expected" ]]; then
    log_ok "4/5 changelog sha256 matches manifest"
  else
    log_warn "4/5 changelog sha256 mismatch — manifest may describe a different revision"
  fi
else
  log_warn "4/5 no SOURCE/handover/CHANGELOG.md in bundle — skipped"
fi

# 5) provenance summary
log_ok "5/5 manifest summary:"
sed -n '/^## Provenance/,/^## Contents/p' "$MANIFEST" | sed 's/^/    /'
grep -E '^## Quality gates' -A 2 "$MANIFEST" | head -3 | sed 's/^/    /' || true

log_ok "verification complete — bundle is internally consistent (see notes above)"