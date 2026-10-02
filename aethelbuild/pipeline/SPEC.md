# AethelBuild — Prototype Delivery Infrastructure (Git-Native Handover Pipeline)

> **Document ID:** ATH-BLD-INF-001
> **Author:** Prometheus (Product & Innovation)
> **Status:** Ratified by Product — pending repo link (owner's repo picker)
> **Companion:** `/home/team/shared/delivery/templates/build-blueprint-template.md` (ATH-BLD-TPL-001, rat. Delphi)

---

## 1. Purpose

AethelBuild sells **vertical-slice AI prototypes** (R30,000–R120,000, 2–4 weeks).
Clients pay for three things: working code, proof of quality, and a clean handover.
This infrastructure makes the third one production-grade and repeatable:

- **Versioned** — every prototype is a SemVer release, recorded as an annotated
  git tag. Versions are never invented; they are read from the repository.
- **Packaged** — every release produces a deterministic, checksummed artifact so
  `what was handed over` is provable weeks or months later.
- **Released** — a release cannot happen until every quality gate (blueprint
  G1–G6) is recorded as passed in the repo itself.
- **Handed over** — a single bundle (source snapshot + artifact + manifest +
  docs) that the client can rebuild, verify and audit independently.

The pipeline is **git-native**: git tags, branches and trees are the source of
truth; no external database or CI server is required. It runs on any repo after
linking (owner's repo picker in progress).

## 2. Repository Model

Every AethelBuild prototype lives in **its own repository** (or a clearly
namespaced directory if the owner links one multi-project repo), with this
layout:

```
prototype-root/
├── README.md                     # what this is, quick start, client-facing
├── handover/
│   ├── CHANGELOG.md              # monotonically appended, never rewritten
│   ├── CONVENTIONS.md            # copy of the branch/tag/commit rules
│   └── release-notes/            # one file per release: v0.1.0.md, v0.2.0.md …
├── quality-gates/
│   └── gate-checklist.yaml       # machine-readable G1–G6 status (the release key)
├── docs/
│   ├── architecture.md           # diagram + narrative (blueprint §3)
│   ├── api.md                    # endpoint reference
│   ├── performance.json          # blueprint §6.2 baseline
│   ├── security-report.md        # G4 evidence
│   ├── compliance.md             # G5 evidence (POPIA/GDPR)
│   ├── adr/                      # architecture decision records
│   └── production-roadmap.md     # prototype → production transition plan
├── deploy/                       # compose/manifests, env.example (NO real secrets)
├── src/ …tests/ …                # the prototype itself
├── .gitignore                    # blocks secrets, artifacts, local env
└── env.example                   # documented placeholders only
```

### 2.1 Canonical workflow

```
feature/<slug>  ──►  main (integration, always green)
                         │  ab-gates.sh + ab-version.sh
                         ▼
                 release/vX.Y.Z  ──►  ab-package.sh + ab-release.sh (tag)
                         │
                         ▼
                 ab-handover.sh  ──►  ab-handover-<client>-vX.Y.Z-<date>.zip
```

## 3. Versioning (SemVer + tags)

- Format: `MAJOR.MINOR.PATCH`, optionally `-pre.N` / `-rc.N` pre-release suffix.
- **Version source of truth: the latest `ab-prototype-v*` tag.**
- Rules:
  - `0.x` while the prototype is in iterative build (normal for AethelBuild).
  - `1.0.0` at first formal handover cut (client-ready snapshot).
  - PATCH: bugfixes on a released snapshot; MINOR: new capability, backward
    compatible; MAJOR: breaking change / new milestone.
- Tag naming: `ab-prototype-vX.Y.Z` (annotated, with release notes summary).
  Example: `ab-prototype-v1.0.0`.
- `handover/CHANGELOG.md` is appended by `ab-version.sh` at each bump — the
  changelog and the tag can never drift because the script does both commit and
  tag atomically (tag points at the commit that wrote the changelog entry).

## 4. Branching

| Branch | Purpose | Rules |
|---|---|---|
| `main` | Integration; single green line | PRs only outside the pipeline; every commit passes build/tests |
| `feature/<slug>` | Workstreams (data, pipeline, API, hardening) | Short-lived; merged via review |
| `release/vX.Y.Z` | Release candidate for a version | Created by `ab-release.sh`; only gate-evidence/doc fixes land here |
| `handover/vX.Y.Z` | Frozen client deliverable | Created at handover time; never receives further commits |

Handover branch = the exact commit clients are given. `ab-handover.sh` creates
it from the release tag so provenance is one commit SHA.

## 5. Quality Gates (enforced, not advisory)

Mirrors blueprint §6.1. Status lives in `quality-gates/gate-checklist.yaml` so
the release script can refuse to proceed:

| Gate | Criterion | Evidence file | Owner |
|---|---|---|---|
| G1 Architecture | Matches blueprint; ADRs for deviations | `docs/adr/` | Delphi |
| G2 Functional | Vertical-slice E2E passes (synthetic data) | test report | Prometheus |
| G3 Performance | P99 < 2 s @ 10 concurrent; baseline recorded | `docs/performance.json` | Prometheus |
| G4 Security | No critical/high CVEs; semgrep clean; dep audit clean | `docs/security-report.md` | Sentinel |
| G5 Compliance | No PII in logs; sanitization verified; cross-border flow documented | `docs/compliance.md` | Aegis |
| G6 Handover pkg | README, deploy guide, architecture, API, ADR, roadmap | the repo itself | Delphi |

`ab-release.sh` parses the YAML checklist and aborts unless every gate is
`pass`. Evidence files listed in the checklist must exist on disk, or the gate
counts as failed.

## 6. Packaging

`ab-package.sh` produces, per release:

```
ab-prototype-<name>-vX.Y.Z-<sha7>.tar.gz     # runtime + src + docs (no .git, no artifacts)
ab-prototype-<name>-vX.Y.Z-<sha7>.tar.gz.sha256
```

- Deterministic tar (sorted names, fixed mtime via `SOURCE_DATE_EPOCH` when set,
  no uid/gid) so re-packing the same tag yields the same file where possible.
- **Secrets scan**: script refuses to package if any tracked file matches the
  secret patterns (live keys, credentials, private key headers). A `password`
  or `secret` file present outside `*.example` also blocks.
- `.git`, build output, node_modules, `.env`, and prior artifacts are excluded.

## 7. Release

`ab-release.sh` (idempotent, safe to re-run):

1. Working tree must be clean.
2. `ab-gates.sh` — all G1–G6 listed as `pass` + evidence files present.
3. Version bump via `ab-version.sh <major|minor|patch> [-p prerelease]` →
   writes CHANGELOG + `handover/release-notes/vX.Y.Z.md`, commits.
4. **Package first** — `ab-package.sh` from HEAD (secret scan + artifact). If
   this fails, **no tag is created**: a leaked secret can never be enshrined
   in a release tag.
5. Creates `release/vX.Y.Z` branch.
6. Annotated tag `ab-prototype-vX.Y.Z` on the release commit.
7. Prints the release summary (version, tag SHA, artifact path + checksum).

Because step 3 commits and step 6 tags the same commit, tag ↔ changelog ↔
artifact provenance is one SHA.

## 8. Handover

`ab-handover.sh [-c <client>] [-v <version>]` assembles:

```
ab-handover-<client>-vX.Y.Z-<YYYYMMDD>.zip
├── SOURCE/                     # git archive of the handover branch (tag tree)
├── ARTIFACT/                   # the .tar.gz + .sha256 from §6
├── MANIFEST.md                 # provenance record (see below)
├── RELEASE_NOTES.md            # client-facing notes
└── docs/                       # architecture, api, performance, roadmap
```

Every bundle also gets `<bundle>.sha256` (checksum of the zip itself).

### 8.1 Manifest (provenance record) — always populated, never hand-written

| Field | Source |
|---|---|
| Client / engagement | `-c` argument or `AB_CLIENT` env |
| Prototype name | `project.name` from the repo (`handover/project.yaml`) |
| Version + tag | `ab-prototype-vX.Y.Z` tag |
| Release commit SHA | tag object resolve |
| Handover branch SHA | `handover/vX.Y.Z` head |
| Changelog hash | `handover/CHANGELOG.md` sha256 |
| Gate results | `quality-gates/gate-checklist.yaml` (included verbatim) |
| Artifact checksums | ARTIFACT/SHA256SUMS |
| Bundle sha256 | `.sha256` sidecar |
| Repo URL | `git remote get-url origin` (omit if unlinked) |
| Builder / date | `$AB_BUILDER` (defaults to real username) / `%Y-%m-%dT%H:%M:%SZ` UTC |

## 9. Secrets & Compliance (hard rules)

- **Never** commit `.env`, real keys, tokens, model API credentials, or PII.
  `env.example` only. `.gitignore` template is shipped in the kit.
- Packaging and handover both run a scan; live-key patterns are a release
  blocker. This is a hard stop, not a warning.
- POPIA/GDPR: G5 evidence must cover data handling for the engagement's data
  scope before any release. Prototypes ship with sanitized synthetic data only.
- The bundle is **not** encrypted by default (it carries no secrets — that is
  the point). If a client requires encryption, encrypt the zip out-of-band
  (e.g., age/gpg) and record the method in the manifest, never the key.

## 10. Verification & Audit

`ab-verify.sh <bundle.zip>` (client-side or on our side):

- Checks zip checksum (sidecar), re-extracts, recomputes ARTIFACT sha256 and
  `SHA256SUMS`, compares the handover commit SHA against the tag, and reports a
  pass/fail summary. Anyone with the bundle can independently confirm it is
  exactly what Aethelgard released — no CI, no private infra required.

## 11. Install into a real repo

```bash
# after the owner links the repo and we have origin set:
kit=/home/team/shared/products/aethelbuild-delivery-infrastructure
cp "$kit"/handover/CONVENTIONS.md   ./
mkdir -p handover/scripts quality-gates docs/adr deploy
cp "$kit"/handover/scripts/ab-*.sh  handover/scripts/
cp "$kit"/quality-gates/gate-checklist.yaml quality-gates/
cp "$kit"/handover/templates/*.tpl  handover/templates/  # + CHANGELOG.md
chmod +x handover/scripts/*.sh
# scaffold per-project name:
./handover/scripts/ab-init.sh <prototype-name>
git add -A && git commit -m "chore: install AethelBuild delivery pipeline (v0.1.0)"
```

## 12. Out of scope / next steps

- **Repo link**: pending the owner's repo picker. The kit is remote-agnostic;
  `origin` URL is read only for the manifest and skipped when absent.
- CI automation (GitHub Actions workflow) can be added after linking; every
  script is CI-safe (pure git + coreutils, no TTY prompts).
- Per-client access control (who may push tags) is enforced via the hosting
  platform's branch protections once the repo exists.

## 13. Version Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-09-22 | Prometheus | Initial spec: repository model, SemVer+tags, branching, G1–G6 enforcement, packaging, release, handover bundle, secrets policy, verification |