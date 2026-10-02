# AethelBuild Delivery Pipeline — Intake → Support

**Sign-off key:** E = engineer (delivery lead) · D = design/delivery lead (Delphi/Prometheus) · O = owner · C = client

| # | Stage | Entry criteria | Work | Exit criteria / DOD gate | Sign-off |
|---|---|---|---|---|---|
| 1 | **Intake** | Lead in CRM; scope call done | Record engagement in CRM; confirm tier (Enterprise/Professional/Standard), POPIA consent, data scope | ENGAGEMENT.yaml created; audit ref linked; no code yet | E, O |
| 2 | **Charter** | Intake done | Charter signed (MSA/NDA/SLA per aegis templates); success metrics; synthetic-data rule agreed | Charter committed to `docs/adr/`; client named in CRM | E, O, C |
| 3 | **Build** | Charter signed | Vertical slice in `src/` (Python/FastAPI backend, Triton/vLLM integration via `src/inference/`, optional TS frontend); ADRs for deviations; **synthetic data only** | `ruff` clean; unit tests green; feature/branch merged to `main` | E |
| 4 | **Qualify** | Build done | Performance baseline (`docs/performance.json`: P99<2s @10 concurrent where applicable); security scan (Semgrep + dep audit); compliance evidence (POPIA/GDPR: no PII in logs/fixtures) | G1–G6 evidence files exist; gates recorded in `docs/quality-report.md` | E, D |
| 5 | **Package** | Qualify passed | SemVer bump; CHANGELOG entry; `releases/` tarball + sha256 (CI or `scripts/ci-local.sh` + `build_handover.sh -v`) | Artifact builds reproducibly; secret scan clean **before tag** | E |
| 6 | **Review** | Package done | Internal review of code + evidence (peer: another engineer; lead: delivery lead) | No open critical/high findings; owner briefed | E, D, O |
| 7 | **Release** | Review passed | Tag `vX.Y.Z` (annotated); GitHub Release with auto notes (`.github/workflows/release.yml`) | Tag exists; release notes generated; artifact attached | E, D |
| 8 | **Handover** | Release done | `scripts/build_handover.sh` → versioned bundle (SOURCE/ARTIFACT/docs/HANDOVER.md + sha256) | Bundle verifies (`sha256sum -c`); acceptance checklist delivered; client sign-off collected | E, O, C |
| 9 | **Support** | Handover accepted | Support window (ENGAGEMENT.yaml `support_window_days`, default 30) via iitaethelgard@outlook.com; severity triage; fixes released as patch tags | Window closed or extension agreed; CRM updated; retrospective note | E, O |

**DOD invariant:** no stage may be skipped; a stage's exit criteria are the next
stage's entry criteria. Release is blocked unless Qualify evidence is committed.
