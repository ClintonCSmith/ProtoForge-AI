#!/usr/bin/env bash
# ab-init.sh — scaffold a new AethelBuild prototype repository at v0.1.0.
# Usage: ab-init.sh <prototype-name> [--client <name>]
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=ab-common.sh
source "$SCRIPT_DIR/ab-common.sh"

[[ $# -ge 1 && $1 != -* ]] || die "usage: ab-init.sh <prototype-name> [--client <name>]"
PROTO_NAME=$1; shift
CLIENT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client) CLIENT=$2; shift 2;;
    *) die "unknown argument: $1";;
  esac
done
[[ $PROTO_NAME =~ ^[a-z0-9][a-z0-9-]*$ ]] \
  || die "prototype name must match ^[a-z0-9][a-z0-9-]*$ (got: '$PROTO_NAME')"

TEMPLATES="$SCRIPT_DIR/../templates"

# Init git if needed (don't clobber an existing repo)
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init -q -b main
  log_ok "initialized new git repository on branch 'main'"
fi
# Scaffolding is safe over untracked files; only warn if tracked changes exist
if ! git diff --quiet 2>/dev/null; then
  log_warn "tracked changes detected — scaffolding into the current tree (commit after)"
fi

mkdir -p handover/release-notes handover/templates quality-gates docs/adr deploy src tests

# project.yaml
if [[ ! -f handover/project.yaml ]]; then
  sed -e "s/{{PROTOTYPE_NAME}}/$PROTO_NAME/g" \
      -e "s/{{CLIENT_PLACEHOLDER}}/${CLIENT:-TBD}/g" \
      "$TEMPLATES/project.yaml.tpl" > handover/project.yaml
  log_ok "wrote handover/project.yaml (name=$PROTO_NAME)"
fi

# gate checklist (create if missing, always substitute the project name)
if [[ ! -f quality-gates/gate-checklist.yaml ]]; then
  if [[ -f "$SCRIPT_DIR/../../quality-gates/gate-checklist.yaml" ]]; then
    cp "$SCRIPT_DIR/../../quality-gates/gate-checklist.yaml" quality-gates/gate-checklist.yaml
  else
    die "quality-gates/gate-checklist.yaml missing and no kit copy found — re-run the kit install"
  fi
fi
sed -i "s/{{PROTOTYPE_NAME}}/$PROTO_NAME/g" quality-gates/gate-checklist.yaml
log_ok "wrote quality-gates/gate-checklist.yaml"

# changelog
if [[ ! -f handover/CHANGELOG.md ]]; then
  sed "s/{{PROTOTYPE_NAME}}/$PROTO_NAME/g; s/{{DATE_UTC}}/$(date -u +%Y-%m-%d)/g" \
      "$TEMPLATES/CHANGELOG.md.tpl" > handover/CHANGELOG.md
  log_ok "wrote handover/CHANGELOG.md"
fi

# conventions + gitignore + env example + README stub
[[ -f CONVENTIONS.md ]] || cp "$TEMPLATES/../CONVENTIONS.md" ./CONVENTIONS.md 2>/dev/null || true
if [[ ! -f .gitignore ]]; then
  cp "$TEMPLATES/gitignore.tpl" .gitignore
  log_ok "wrote .gitignore"
fi
[[ -f env.example ]] || cat > env.example <<'EOF'
# Copy to .env for local development. NEVER commit .env.
# One placeholder per integration; values come from the engagement's secret vault.
MODEL_API_KEY=
VECTOR_DB_URL=
INFERENCE_BASE_URL=http://localhost:8000
EOF

if [[ ! -f README.md ]]; then
  cat > README.md <<EOF
# ${PROTO_NAME}

Vertical-slice AI prototype delivered by **IIT Aethelgard (Pty) Ltd** via the
AethelBuild rapid prototyping engagement (see CONVENTIONS.md and
handover/CHANGELOG.md).

## Quick start
1. \`cp env.example .env\` and fill from the engagement vault.
2. Run the stack (\`docker compose up\` or \`make dev\`).
3. Smoke test: \`pytest tests/\`

## Delivery pipeline
\`handover/scripts/ab-gates.sh && handover/scripts/ab-release.sh patch\` then
\`handover/scripts/ab-handover.sh -c <client>\`.
EOF
  log_ok "wrote README.md"
fi

# first release notes for the scaffold
if [[ ! -f handover/release-notes/v0.1.0.md ]]; then
  mkdir -p handover/release-notes
  sed -e "s/{{PROTOTYPE_NAME}}/$PROTO_NAME/g" \
      -e "s/{{VERSION}}/0.1.0/g" \
      -e "s/{{DATE_UTC}}/$(date -u +%Y-%m-%dT%H:%M:%SZ)/g" \
      -e "s/{{BUILDER}}/$(builder_name)/g" \
      "$TEMPLATES/RELEASE_NOTES.md.tpl" > handover/release-notes/v0.1.0.md
fi

log_ok "AethelBuild scaffold complete — next: set quality-gates to 'pass' with evidence, then ab-version.sh / ab-release.sh"