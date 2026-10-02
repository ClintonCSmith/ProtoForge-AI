# AethelBuild — delivery system (IIT Aethelgard)

**This repository (`ProtoForge-AI`) is the owner-linked AethelBuild
client-delivery home.** New client engagements are scaffolded under
`aethelbuild/deliveries/<client-slug>/`; each is a self-contained git repo
(remote added only when the client repo is supplied) containing the
vertical-slice prototype for that engagement.

| Path | Purpose |
|---|---|
| `PIPELINE.md` | 9-stage delivery pipeline (Intake→Support), DOD gates, sign-offs |
| `RELEASING.md` | SemVer + tag + CI release runbook |
| `IP-AND-COMPLIANCE.md` | IP split, work-product clause, POPIA-safe rules |
| `scaffold/` | Client-delivery repo skeleton (src/tests/infra/docs/scripts/.github) |
| `scripts/new_engagement.sh` | Scaffold a new engagement into `deliveries/<slug>/` (git init, NO remote) |
| `scripts/build_handover.sh` | Versioned handover bundle (tarball + zip + sha256) |
| `templates/HANDOVER.md.tpl` | Bundle manifest template |
| `pipeline/` | Ratified git-native handover pipeline kit (SPEC.md, ab-* scripts, quality gates) |

Run a handover end-to-end: `scripts/new_engagement.sh <client-slug>`, build the
slice, `git tag vX.Y.Z`, `scripts/build_handover.sh -v X.Y.Z`. Full runbook in
`README` of the system kit (shared workspace) and PIPELINE.md above.
