# RELEASING.md — git release workflow (AethelBuild)

## Versioning (SemVer)
- Tags: `vMAJOR.MINOR.PATCH` (annotated). `git tag -a v0.1.0 -m "..."`.
- 0.x during build; v1.0.0 at first handover cut; PATCH = accepted-fix on a
  released snapshot; MINOR = new capability; MAJOR = breaking milestone.

## Local pre-flight (every release)
```bash
./scripts/ci-local.sh            # ruff + pytest (mirror of CI)
# set gates to pass with evidence committed (docs/quality-report.md)
git tag -a v0.1.0 -m "first client-ready slice"
scripts/build_handover.sh -v 0.1.0   # secret scan runs BEFORE bundling
```
**Order matters:** run the secret scan (build_handover does) before tagging a
release; a leaked credential must never be enshrined in a tag. If a scan hits,
fix by moving the value to `env.example`/`examples/`, commit, re-tag.

## CI (`.github/workflows/release.yml`)
- Trigger: push of `v*` tag (or workflow_dispatch).
- `test`: Python 3.11 · `pip install -e ".[dev]"` · `ruff check src tests` ·
  `pytest` · secret scan (live-key patterns are a hard fail).
- `package`: deterministic tarball + sha256, uploaded as artifact.
- `release`: `gh release create <tag> artifacts/* --generate-notes`.
- Optional commented `docker` job for Triton/vLLM serving images (GHCR).
- Actions pinned to major versions (`checkout@v4` etc.), fork-safe
  (`github.token`, no third-party secrets).

## Tag → release discipline
1. All Qualify evidence committed on `main`.
2. Tag `vX.Y.Z` at the release commit.
3. CI builds+tests+packages that exact tag.
4. `build_handover.sh` freezes the bundle from the tag.
5. Client handover references tag + commit SHA (never an unpinned branch).
