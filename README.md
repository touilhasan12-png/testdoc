# TrueCrime_Sample_01 — production repository

Case: **THE SODDER CHILDREN** — Fayetteville, West Virginia, 25 December 1945. Unsolved.
Deliverable: one ~5 minute English documentary pilot, 1080p, neo-noir archival look.

This repository is the **execution floor**. The producer agent works in a separate orchestration
environment and never installs or runs production tools there; everything runs here through
GitHub Actions (`workflow_dispatch`).

## Layout

```
.github/workflows/   tc01_smoke.yml (runner check) · tc01_pipeline.yml (stages 1-12)
project/             case brief, tool policy, 50-tool manifest, plan
tc01/lib/            shared helpers: logging, artefacts, substitutes for removed tools
tc01/stages/sNN_*/   one folder per production stage
work/                runtime output (git-ignored); published as Actions artefacts
```

`pipeline/`, `tools/`, `requirements*.txt` and `.github/workflows/pipeline.yml` at the root belong to a
**pre-existing, unrelated project** (case: Mary Celeste) that was already in this repository. They are left
completely untouched. This production lives entirely under the `tc01/` namespace.

## Hard rules

- English only inside the video. No Arabic string may reach a frame, a title, a caption or a voice track.
- No credential of any kind is committed, printed or logged. `.secrets/`, `*.token`, `work/` are ignored.
- Every factual claim carries a source that was archived before use. No source, no claim.
- On-screen disclosures: `Archival photo` · `Reenactment` · `Colourised reconstruction` · `Re-created`.
- No tool output is ever faked. A tool that fails is recorded as failed and worked around.
- Tool policy and the removal/substitute register: `project/00_tool_policy_v1.md`.

## Artefacts

Each stage uploads its own artefact (`tc01_sNN_*`). The orchestration agent downloads them, pushes them to
Google Drive (`TrueCrime_Sample_01/`) and appends a line to `07_logs` and to `project/00_tools_manifest_v1.json`.
