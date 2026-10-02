# AethelBuild — Repository Conventions (branch / tag / commit)

Companion to SPEC.md (ATH-BLD-INF-001). Keep this file at the repo root of every
AethelBuild prototype.

## Tags
- Version tags: `ab-prototype-v<MAJOR>.<MINOR>.<PATCH>` (annotated: `git tag -a`).
- Never move, delete, or rewrite a version tag. `git tag -l 'ab-prototype-v*'` is
  the version history of the engagement.
- Pre-release: `ab-prototype-v1.0.0-rc.1` style allowed pre-handover.

## Branches
| Branch | Lifetime | Created by | Merges into |
|---|---|---|---|
| `main` | permanent | — | — |
| `feature/<slug>` | short | engineers | `main` (PR + review) |
| `release/vX.Y.Z` | until released | `ab-release.sh` | `main` |
| `handover/vX.Y.Z` | permanent/frozen | `ab-handover.sh` | never |

Rules:
- `main` must stay green: build + tests pass on every commit.
- Only gate-evidence or documentation fixes land on a `release/*` branch.
- A `handover/*` branch is the exact deliverable; committing to it after
  handover invalidates the manifest — recreate the branch, re-tag, re-bundle.

## Commits
- Conventional prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `perf:`,
  `security:`, `refactor:`.
- One concern per commit; reference the issue/gate where relevant
  (e.g. `fix: correct RAG chunk overlap (G2)`).
- Changelog entries are machine-appended by `ab-version.sh` — never edit
  `handover/CHANGELOG.md` by hand in a way that rewrites history.

## Release contract (enforced by scripts, not by memory)
1. Working tree clean.
2. `quality-gates/gate-checklist.yaml`: every gate `pass` with evidence files
   existing on disk.
3. `ab-version.sh` bumps, appends CHANGELOG + release notes, commits.
4. `ab-release.sh` tags the bump commit; `ab-package.sh` builds the artifact.
5. `ab-handover.sh` freezes `handover/vX.Y.Z` and builds the client bundle.

## Secrets
- `.gitignore` must block `.env`, `*.pem`, `*.key`, credentials, artifacts dirs.
- A secret scan blocks release/package; a hit that is a false positive is fixed
  by moving the file to `examples/` and re-adding, not by bypassing the scan.