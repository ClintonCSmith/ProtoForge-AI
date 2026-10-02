#!/usr/bin/env bash
# ab-common.sh — shared helpers for the AethelBuild handover pipeline.
# Sourced by ab-init, ab-version, ab-gates, ab-package, ab-release,
# ab-handover, ab-verify. Not meant to be executed directly.
set -euo pipefail

# ---- Logging ---------------------------------------------------------------
AB_COLOR=${AB_COLOR:-auto}
if [[ $AB_COLOR == "auto" && -t 2 ]]; then
  C_RED=$'\033[31m'; C_GRN=$'\033[32m'; C_YLW=$'\033[33m'; C_BLU=$'\033[34m'; C_OFF=$'\033[0m'
else
  C_RED=""; C_GRN=""; C_YLW=""; C_BLU=""; C_OFF=""
fi
log_info()  { printf '%s[ab]%s %s\n' "$C_BLU" "$C_OFF" "$*"; }
log_ok()    { printf '%s[ab]%s %s\n' "$C_GRN" "$C_OFF" "$*"; }
log_warn()  { printf '%s[ab]%s %s\n' "$C_YLW" "$C_OFF" "$*" >&2; }
log_err()   { printf '%s[ab]%s %s\n' "$C_RED" "$C_OFF" "$*" >&2; }
die()       { log_err "$*"; exit 1; }

# ---- Repo discovery --------------------------------------------------------
require_git_repo() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || die "not inside a git repository — run this from the prototype repo root"
}
require_clean_tree() {
  [[ -z "$(git status --porcelain)" ]] \
    || die "working tree is not clean — commit or stash changes first"
}

# ---- Project identity ------------------------------------------------------
# Reads handover/project.yaml (created by ab-init). Returns via globals.
AB_PROJECT_NAME=""
AB_PROJECT_FILE=""
load_project() {
  require_git_repo
  local candidates=(handover/project.yaml project.yaml)
  local f=""
  for f in "${candidates[@]}"; do
    [[ -f $f ]] && { AB_PROJECT_FILE=$f; break; }
  done
  [[ -n $AB_PROJECT_FILE ]] || die "project.yaml not found — run ab-init.sh first"
  AB_PROJECT_NAME=$(sed -n 's/^name:[[:space:]]*//p' "$AB_PROJECT_FILE" | tr -d '"'"'"' ' | head -1)
  [[ -n $AB_PROJECT_NAME ]] || die "project.name missing in $AB_PROJECT_FILE"
}

# ---- Versioning ------------------------------------------------------------
AB_TAG_PREFIX=ab-prototype-v
AB_VERSION=""          # next version (e.g. 0.1.0) — set by next_version()
AB_FULL_VERSION=""     # version incl. pre-release suffix (e.g. 0.1.0-rc.1)

latest_version_tag() {
  # highest existing version tag by SemVer; echoes tag or empty string
  git tag -l "${AB_TAG_PREFIX}*" | sed "s/^${AB_TAG_PREFIX}//" \
    | sort -V | tail -1
}

# next_version <major|minor|patch> [--pre <suffix>]
# Computes AB_FULL_VERSION. Pure bash; no external semver lib.
next_version() {
  local bump=$1 pre=""
  if [[ ${2:-} == "--pre" ]]; then
    [[ -n ${3:-} ]] || die "--pre requires a suffix (e.g. rc.1, preview.2)"
    pre=$3
  fi
  case "$bump" in major|minor|patch) ;; *) die "bump must be major|minor|patch (got: $bump)";; esac

  local cur latest
  latest=$(latest_version_tag) || true
  # scaffold baseline is v0.1.0 (see ab-init); bumping before any tag bumps it
  cur=${latest:-0.1.0}

  # strip any pre-release from current for base arithmetic
  local base maj min pat
  base=${cur%%-*}
  IFS=. read -r maj min pat <<<"$base"
  maj=${maj#v}; maj=${maj:-0}; min=${min:-0}; pat=${pat:-0}
  case "$maj" in ''|*[!0-9]*|*[!0-9]*) die "unparseable current version '$cur'";; esac
  case "$min" in ''|*[!0-9]*|*[!0-9]*) die "unparseable current version '$cur'";; esac
  case "$pat" in ''|*[!0-9]*|*[!0-9]*) die "unparseable current version '$cur'";; esac

  local next
  case "$bump" in
    major) next="$((maj+1)).0.0";;
    minor) next="$maj.$((min+1)).0";;
    patch) next="$maj.$min.$((pat+1))";;
  esac

  if [[ -n $pre ]]; then
    # pre-release of the base we are moving to
    AB_FULL_VERSION="$next-$pre"
  else
    AB_FULL_VERSION="$next"
  fi
  AB_VERSION="$next"
}

validate_version() {
  [[ $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]] \
    || die "invalid version '$1' (expected SemVer like 1.0.0 or 1.0.0-rc.1)"
}

# ---- Changelog -------------------------------------------------------------
AB_CHANGELOG=handover/CHANGELOG.md

append_changelog() {
  local version=$1 message=${2:-"No changelog message provided."}
  local dir
  dir=$(dirname "$AB_CHANGELOG")
  mkdir -p "$dir"
  local date_utc
  date_utc=$(date -u +%Y-%m-%d)

  if [[ ! -f $AB_CHANGELOG ]]; then
    cat > "$AB_CHANGELOG" <<EOF
# Changelog — ${AB_PROJECT_NAME}

All notable changes to this prototype. Appended by ab-version.sh.

EOF
  fi

  # insert the new release just before the [Unreleased] section
  local tmp
  tmp=$(mktemp)
  {
    awk -v ver="$version" -v date="$date_utc" '
      /^## \[Unreleased\]/ { printf "## [v%s] — %s\n### Added\n- %s\n\n", ver, date, msg }
      { print }
    ' msg="$message" "$AB_CHANGELOG"
  } > "$tmp" && mv "$tmp" "$AB_CHANGELOG"
}

# ---- Date / builder helpers ------------------------------------------------
utc_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
stamp_date() { date -u +%Y%m%d; }
builder_name() { echo "${AB_BUILDER:-$(whoami 2>/dev/null || echo builder)}"; }