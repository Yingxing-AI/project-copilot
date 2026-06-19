# Roadmap

## Current Direction

Project Copilot is the project memory layer for Codex.

- Codex develops.
- Git versions.
- Project Copilot remembers why.

## v0.3 Direction Convergence

- [x] Reposition from project workflow runner to Codex project memory layer
- [x] Stop GitHub sync, release, and OSS preparation workflows
- [x] Keep natural-language intent dispatch, but stop reinforcing command-system UX
- [x] Add `.ai/adr/` for long-lived decisions
- [x] Add `.ai/sessions/` for Session Memory candidates
- [x] Change close-day flow to candidate confirmation instead of automatic memory expansion
- [x] Generate Codex rules around MVP guardrails, ADR, and Session Memory
- [x] Keep validation data derived from real `.ai` files

## v0.4 Memory Quality

- [x] Converge `check_project` into Memory Health Summary
- [x] Merge `show_roadmap` into `check_project` as a compatibility alias
- [x] Rebuild `timeline_project` around ADR, history, and Session Archive
- [x] Generate derived memory metrics in `.ai/derived/metrics.json`
- [ ] Migrate important historical `DECISIONS.md` entries into ADR files
- [ ] Reduce `ROADMAP.md`, `WORKLOG.md`, and `MEMORY.md` noise in generated templates
- [ ] Improve session candidate extraction rules
- [ ] Improve validation metrics for ADR quality, memory noise, and MVP drift
- [ ] Update demo assets to match Session Memory

## v0.5 Stable Memory Format

- [ ] Stabilize `.ai/adr/` template and numbering rules
- [ ] Stabilize `.ai/sessions/` archive format
- [ ] Make validation reports fully derived from project `.ai` snapshots
- [ ] Provide migration guidance for projects using the older Secretary UX structure

## Explicitly Paused

- MCP integration
- AI Provider integration
- Plugin system
- GitHub sync workflow
- Release workflow
- OSS preparation workflow
- Commit, push, tag, testing, or code modification workflows
