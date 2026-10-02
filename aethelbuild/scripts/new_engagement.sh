#!/usr/bin/env bash
# new_engagement.sh — scaffold a client delivery repo from the AethelBuild
# scaffold. Usage: new_engagement.sh <client-slug> [--name "Client Name"]
# [--tier Enterprise|Professional|Standard] [--audit <ref>] [--crm <ref>]
# [--support <days>] -- remote is NOT added; git is initialized, nothing pushed.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AETHELBULD_ROOT=$(dirname "$HERE")
SCAFFOLD="$AETHELBULD_ROOT/scaffold"
DELIVERIES="${AETHELBULD_ROOT}/deliveries"

SLUG="${1:-}"; NAME="$SLUG"; TIER=Enterprise; AUDIT=; CRM=; SUPPORT=30; PROTOTYPE="ai-prototype"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME=$2; shift 2;; --tier) TIER=$2; shift 2;;
    --audit) AUDIT=$2; shift 2;; --crm) CRM=$2; shift 2;;
    --support) SUPPORT=$2; shift 2;; --prototype) PROTOTYPE=$2; shift 2;;
    -*) echo "unknown: $1" >&2; exit 1;; *) SLUG=$1; shift;;
  esac
done
[[ -n $SLUG ]] || { echo "usage: new_engagement.sh <client-slug> [opts]" >&2; exit 1; }
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "slug must match ^[a-z0-9][a-z0-9-]*$" >&2; exit 1; }
[[ -d $SCAFFOLD ]] || { echo "scaffold missing at $SCAFFOLD" >&2; exit 1; }

DEST="$DELIVERIES/$SLUG"
[[ ! -e $DEST ]] || { echo "delivery already exists: $DEST" >&2; exit 1; }
mkdir -p "$DELIVERIES"
cp -r "$SCAFFOLD" "$DEST"
find "$DEST" -type f -not -path "*/.git/*" -exec sed -i \
  -e "s/{{CLIENT_NAME}}/$NAME/g" \
  -e "s/{{CLIENT_SLUG}}/$SLUG/g" \
  -e "s/{{DATE}}/$(date -u +%Y-%m-%d)/g" \
  -e "s/{{TIER}}/$TIER/g" \
  -e "s/{{AUDIT_REF}}/${AUDIT:-TBD}/g" \
  -e "s/{{CRM_REF}}/${CRM:-TBD}/g" \
  -e "s/{{SUPPORT_DAYS}}/$SUPPORT/g" \
  -e "s/{{PROTOTYPE}}/$PROTOTYPE/g" {} +
chmod +x "$DEST/scripts/ci-local.sh"
(cd "$DEST" \
  && git init -q -b main \
  && { git config user.email >/dev/null 2>&1 || git config user.email "delivery@iitaethelgard.local"; } \
  && { git config user.name  >/dev/null 2>&1 || git config user.name  "IIT Aethelgard Delivery"; } \
  && git add -A \
  && git commit -q -m "chore: scaffold AethelBuild delivery for $NAME")
echo "created $DEST (git initialized, NO remote added)"
echo "next: push to the client repo when provided by the owner; then build the vertical slice."
