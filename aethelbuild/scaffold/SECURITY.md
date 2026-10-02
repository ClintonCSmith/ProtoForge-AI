# Security

- Zero-trust: every service authenticates; no network trust boundaries assumed.
- Secrets: only via environment (vault-injected at deploy); `.env` is never
  committed; live keys in this repo are a release-blocking finding.
- Data: **synthetic data only** in fixtures, tests and demos (POPIA-safe).
  Real client data never enters this repository or its artifacts.
- Reporting: contact iitaethelgard@outlook.com for any security concern.
  No public disclosure before coordination.
