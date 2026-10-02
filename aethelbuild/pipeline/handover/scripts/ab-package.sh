#!/usr/bin/env bash
# ab-package.sh — build a deterministic, checksummed release artifact for the
# given git tree (default: HEAD). Refuses to package if secrets are detected.
# Usage: ab-package.sh [-v <version>] [-o <outdir>] [<tree-ish>]
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=ab-common.sh
source "$SCRIPT_DIR/ab-common.sh"

TREE="HEAD"
OUTDIR=${AB_OUT_DIR:-handover/releases}
VERSION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v) VERSION=$2; shift 2;;
    -o) OUTDIR=$2; shift 2;;
    -*) die "unknown argument: $1";;
    *)  TREE=$1; shift;;
  esac
done

require_git_repo
load_project

# resolve version: caller override, else latest tag, else 0.1.0
if [[ -n $VERSION ]]; then
  validate_version "$VERSION"
else
  latest=$(latest_version_tag || true)
  VERSION=${latest:-0.1.0}
fi

SHA=$(git rev-parse --short=7 "$TREE" 2>/dev/null) || die "cannot resolve tree '$TREE'"
log_info "packaging $TREE ($SHA) as v$VERSION"

# ---- Secrets scan (release blocker) ---------------------------------------
scan_tree() {
  local t=$1 hits=0
  while IFS= read -r f; do
    [[ -n $f ]] || continue
    # skip example/template/docs to avoid false positives on literal patterns
    case "$f" in
      *.example|*.tpl|CONVENTIONS.md|RELEASE_NOTES.md|CHANGELOG.md) continue;;
      docs/*|*.md|*.txt) continue;;
    esac
    if git show "$t:$f" 2>/dev/null | grep -Eq \
        '(AKIA[0-9A-Z]{16}|-----BEGIN (RSA |OPENSSH |EC |PGP )?PRIVATE KEY-----|sk_live_[A-Za-z0-9]{10,}|pk_live_[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35})' \
      ; then
      log_err "  SECRET HIT: $f"
      hits=1
    fi
  done < <(git ls-tree -r --name-only "$t")
  # suspicious filenames (password/secret/credential) outside examples
  while IFS= read -r f; do
    [[ -n $f ]] || continue
    case "$f" in
      *.example|*examples/*|*templates/*) continue;;
    esac
    if [[ $f =~ (^|/)(password|secret|credential|credentials)([^/]*)$ ]]; then
      log_err "  SUSPICIOUS FILE NAME: $f"
      hits=1
    fi
  done < <(git ls-tree -r --name-only "$t")
  [[ $hits == 0 ]] || return 1
  return 0
}

if ! scan_tree "$TREE"; then
  die "secret scan failed — move real credentials to env.example/examples and retry"
fi
log_ok "secret scan clean for $TREE"

# ---- Build artifact --------------------------------------------------------
mkdir -p "$OUTDIR"
ART_NAME="ab-prototype-${AB_PROJECT_NAME}-v${VERSION}-${SHA}.tar.gz"
ART="$OUTDIR/$ART_NAME"

# Deterministic artifact: git archive (stable member order) piped through
# gzip -n (no timestamp header) — re-packing the same tag yields the same file.
rm -f "$ART" "$ART.sha256"
git archive --format=tar --prefix="ab-prototype-${AB_PROJECT_NAME}-v${VERSION}/" "$TREE" \
  | gzip -n -c > "$ART"

[[ -s $ART ]] || die "git archive produced an empty artifact"
tar -tzf "$ART" >/dev/null || die "artifact tarball is corrupt"

sha256sum "$ART" | awk '{print $1}' > "$ART.sha256"
log_ok "artifact:  $ART"
log_ok "sha256:    $(cat "$ART.sha256")"