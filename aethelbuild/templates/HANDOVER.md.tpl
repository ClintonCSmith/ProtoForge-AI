# Handover — {{CLIENT_NAME}} — {{PROTOTYPE}} v{{VERSION}}

Prepared by IIT Aethelgard (Pty) Ltd · {{DATE_UTC}} · Builder: {{BUILDER}}

## 1. What this is
A vertical-slice AI prototype delivered under the AethelBuild engagement.
Scope, acceptance criteria and commercial terms: see the signed Charter/MSA.

## 2. Deliverables in this bundle
- `SOURCE/` — exact source tree at tag `{{TAG}}` (commit {{RELEASE_SHA}})
- `ARTIFACT/` — release tarball + SHA256SUMS
- `docs/` — architecture, API, runbook, ADRs, performance/security/compliance evidence
- `RELEASE_NOTES` summary below

## 3. Provenance
| Item | Value |
|---|---|
| Release tag | `{{TAG}}` |
| Release commit | {{RELEASE_SHA}} |
| Handover branch | `{{HANDOVER_BRANCH}}` ({{HANDOVER_SHA}}) |
| Artifact | {{ARTIFACT_NAME}} (SHA256 {{ARTIFACT_SHA256}}) |
| Changelog SHA256 | {{CHANGELOG_SHA256}} |

## 4. How to run
See `docs/runbook/RUNBOOK.md` and `env.example`. Copy `env.example` → `.env`
and fill from the engagement vault. Verify: `sha256sum -c SHA256SUMS` then
`pytest`.

## 5. Acceptance checklist (client sign-off)
- [ ] Source archive extracts and builds (`pip install -e .`, tests pass)
- [ ] Vertical slice runs per runbook on provided/acceptable infra
- [ ] Synthetic-data guarantee: no real client data in fixtures/demos (see IP-AND-COMPLIANCE.md)
- [ ] Performance baseline (docs/performance.json) reviewed
- [ ] Security & compliance evidence reviewed (docs/security-report.md, docs/compliance.md)
- [ ] Support window terms accepted (below)

## 6. Support window
- Support window: {{SUPPORT_DAYS}} days from acceptance, business days,
  async channel (iitaethelgard@outlook.com), severity-based response.
- Excluded: changes outside the agreed scope; environment issues on client
  infrastructure; production data incidents.

## 7. IP notice
This bundle contains proprietary work product of IIT Aethelgard and the
Client's deliverable code. See IP-AND-COMPLIANCE.md in `SOURCE/` for the
ownership split. No license is granted by delivery alone.
