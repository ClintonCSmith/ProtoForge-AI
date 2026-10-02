#!/usr/bin/env bash
# ab-gates.sh — enforce the AethelBuild quality gates (blueprint G1–G6).
# Reads quality-gates/gate-checklist.yaml; every gate must be 'pass' AND its
# evidence file/dir must exist. Exit 0 = release-ready.
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=ab-common.sh
source "$SCRIPT_DIR/ab-common.sh"

require_git_repo
GATES_YAML=quality-gates/gate-checklist.yaml
[[ -f $GATES_YAML ]] || die "missing $GATES_YAML — run ab-init.sh or install the kit"

# Minimal YAML reader for the fixed template shape:
#   gates:\n  g1:\n    id: G1\n    status: pending\n    evidence: docs/…
# Tracks current gate block, then prints "<id>|<status>|<evidence>".
read_gates() {
  awk '
    /^[[:space:]]*g[0-9]+:/ { block=$1; sub(/:.*/,"",block); id=""; status=""; ev="" }
    /^[[:space:]]*status:[[:space:]]+/ { status=$2 }
    /^[[:space:]]*id:[[:space:]]+/ { id=$2 }
    /^[[:space:]]*evidence:[[:space:]]+/ { ev=$2; sub(/^["'"'"']*/,"",ev); sub(/["'"'"']*$/,"",ev)
      print id "|" status "|" ev }
  ' "$GATES_YAML"
}

declare -a lines=()
while IFS= read -r l; do [[ -n $l ]] && lines+=("$l"); done < <(read_gates)
[[ ${#lines[@]} -gt 0 ]] || die "no gates parsed from $GATES_YAML (template shape changed?)"

fail=0
log_info "quality gate check — ${#lines[@]} gates found"
for l in "${lines[@]}"; do
  id=${l%%|*}; rest=${l#*|}; status=${rest%%|*}; ev=${rest#*|}
  ok=1
  [[ $status == "pass" ]] || { ok=0; reason="status='$status' (need pass)"; }
  if [[ $ok == 1 && -n $ev && ! -e $ev ]]; then
    ok=0; reason="evidence missing: $ev"
  fi
  if [[ $ok == 1 ]]; then
    log_ok   "  GATE $id (${ev:-}): pass"
  else
    log_err "  GATE $id: FAIL — ${reason:-unknown}"
    fail=1
  fi
done

if [[ $fail == 1 ]]; then
  die "quality gates not satisfied — release blocked (see above)"
fi
log_ok "all quality gates satisfied — release allowed"