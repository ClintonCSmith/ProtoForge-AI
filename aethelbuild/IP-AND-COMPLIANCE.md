# IP & Compliance Guard — AethelBuild handovers

## 1. Proprietary IP notice
Every handover bundle ships with this notice (also in `LICENSE.tpl` of each
delivery): the prototype is a **work product of IIT Aethelgard (Pty) Ltd**
delivered under the engagement's MSA/NDA. Delivery does not by itself grant a
license; scope of use is per the signed agreement.

## 2. Work-product clause (what transfers)
Per engagement MSA: code **written for this engagement's vertical slice**
("deliverable code") is the Client's work product, delivered under the agreed
license, upon full payment. Handover includes source, tests, docs, runbook and
env template; container images and model weights transfer per engagement terms.

## 3. What stays ours (framework code)
- The delivery pipeline, scaffold, scripts, CI workflows, evaluation harnesses,
  prompt/agent framework tooling, AethelAudit scorecard methodology.
- Generic utilities and the `src/inference` backend abstraction as authored by
  IIT Aethelgard — licensed to the Client for this engagement, not assigned.

## 4. POPIA-safe rule (hard for every engineer)
- **No real client data in this repository, tests, fixtures, demos or
  examples.** Use synthetic data only (`examples/`, `tests/`).
- No PII in logs; sanitization verified before release (Qualify gate G5).
- Cross-border data flow documented; data scope per charter.
- Violation of this rule is a release blocker and an incident-reportable event.

## 5. Handling violations
If real data is found: stop release, quarantine the file, redact history via
support (force-push only after owner approval), log the incident per the
Incident Response Playbook, then re-run Qualify.
