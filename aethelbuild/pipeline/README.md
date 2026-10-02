# AethelBuild — Prototype Delivery Infrastructure

Production-grade, **git-native** handover pipeline for AethelBuild client
prototypes: versioned, packaged, released and handed over from a real code
repository. Full design: **[SPEC.md](SPEC.md)** · Conventions:
**handover/CONVENTIONS.md**.

## What it provides

| Need | Script | Result |
|---|---|---|
| Scaffold a prototype repo | `ab-init.sh <name>` | SemVer v0.1.0 skeleton (project.yaml, gates, changelog, gitignore, README) |
| Version a release | `ab-version.sh minor` | Next SemVer from git tags + changelog entry, committed |
| Enforce quality gates | `ab-gates.sh` | Refuses release unless blueprint G1–G6 are `pass` with evidence on disk |
| Package an artifact | `ab-package.sh` | Deterministic `.tar.gz` + `.sha256`; secret scan blocks live credentials |
| Cut a release | `ab-release.sh patch` | Gates → bump → `release/vX.Y.Z` → annotated tag → artifact |
| Build client bundle | `ab-handover.sh -c <client>` | Frozen `handover/vX.Y.Z` + zip: SOURCE · ARTIFACT · MANIFEST · docs |
| Verify a bundle | `ab-verify.sh <bundle.zip>` | Client-side checksum + provenance audit, no private infra |

## Install into a repo (once the owner's repo link lands)

```bash
kit=/home/team/shared/products/aethelbuild-delivery-infrastructure
mkdir -p handover/scripts quality-gates docs/adr deploy
cp "$kit"/handover/scripts/ab-*.sh      handover/scripts/
cp "$kit"/handover/templates/project.yaml.tpl handover/templates/   # + other .tpl as needed
cp "$kit"/quality-gates/gate-checklist.yaml quality-gates/
cp "$kit"/handover/CONVENTIONS.md       ./
cp "$kit"/handover/templates/gitignore.tpl .gitignore          # if repo is new
chmod +x handover/scripts/*.sh
./handover/scripts/ab-init.sh <prototype-name>
git add -A && git commit -m "chore: install AethelBuild delivery pipeline"
```

> Note: `handover/templates/` must exist in the repo — `ab-init` and
> `ab-handover` read templates from there. If you prefer to keep the kit
> pristine, simply copy the whole `handover/templates` directory, as above.

Per-engagement runbook:

```bash
# during the build
hack... ; set gates to pass in quality-gates/gate-checklist.yaml ; commit

# at the end of the sprint (blueprint G1–G6 all pass)
./handover/scripts/ab-release.sh patch --message "RAG v1 complete, G2–G6 passed"
./handover/scripts/ab-handover.sh -c "Acme Ventures"
./handover/scripts/ab-verify.sh handover/bundles/ab-handover-Acme\ Ventures-v0.1.0-20260922.zip
```

## Honesty & compliance rules

- **Secret scan is a hard stop** — packaging/release refuses on live keys,
  private-key material, AWS/GCP tokens, and credential-named files.
- Only `env.example` placeholders ship; `.env` is always ignored.
- No PII in prototypes: synthetic data only, per G5.
- The Manifests record repo URL, full commit SHAs, checksums — a client can
  independently reproduce and audit everything.

## Layout

```
SPEC.md                  design authority (read this first)
handover/CONVENTIONS.md  branch/tag/commit rules for every prototype repo
handover/scripts/        the pipeline (bash, git + coreutils + zip only)
handover/templates/      CHANGELOG / RELEASE NOTES / MANIFEST / project.yaml / .gitignore
quality-gates/           machine-readable G1–G6 release key
delivery/                per-role empty dirs preserved for future templates
```

## Constraints

- Bash 4+, git, tar, gzip, sha256sum, zip, unzip — no python, no CI, no net.
- Runs from the prototype repo root; git tags are the version source of truth.
- Branch protections (who may tag / merge to main) are enforced platform-side
  once the repo exists (pending owner's repo picker).