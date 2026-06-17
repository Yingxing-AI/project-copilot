# Roadmap

## v0.3 Alpha

- [x] Natural-language intent recognition
- [x] Workflow engine
- [x] `.ai` project memory
- [x] Project initialization
- [x] Existing-project adoption
- [x] Project health check
- [x] Continue development workflow
- [x] Close day workflow
- [x] OSS readiness check
- [x] OSS preparation workflow
- [x] Interactive CLI
- [x] Command mode
- [x] Unknown intent suggestions
- [x] GitHub sync planning and preflight checks
- [x] One-command GitHub push, tag, and release workflow
- [x] Release dry-run and version/tag consistency checks
- [x] GitHub Actions CI for Python 3.10, 3.11, and 3.12
- [x] OSS product packaging docs
- [x] Pytest baseline: 53 passed

## Codex for Open Source Readiness

- [x] Update installer to the current release tag
- [x] Preserve existing `AGENTS.md` content during adopt/init
- [x] Refresh project-state sync wording around Codex-native memory
- [x] Add `docs/CODEX_FOR_OPEN_SOURCE.md`
- [x] Align contributing docs with `pytest -q`
- [x] Add tests for installer version, AGENTS merge safety, and readiness docs

## Validation System

Status: In Progress

Goal: 验证多个项目的项目记忆价值。

- [x] Create `docs/case-studies/` directory
- [x] Move `ai-recruitment` case study into the multi-project structure
- [x] Add reusable case study template
- [x] Add validation report
- [ ] Add more real project case studies
- [ ] Track cross-project work logs, decisions, and knowledge entries
- [ ] Summarize multi-project validation findings

## Sprint Codex Workflow Guide

- [x] Refactor `docs/CODEX_WORKFLOW.md` from agent behavior rules into a user guide
- [x] Keep behavior rules and guardrails in `AGENTS.md`
- [x] Add repository-level `docs/CODEX_WORKFLOW.md`
- [x] Update generated `docs/CODEX_WORKFLOW.md` template
- [x] Update README and Usage references
- [x] Add tests that generated and repository workflow docs stay aligned

## Sprint Agents Hardening

- [x] Add top-level mission-first rule to `AGENTS.md`
- [x] Add strict MVP guardrail with three explicit user choices
- [x] Add target-user mismatch handling
- [x] Add historical decision conflict handling
- [x] Add mandatory `DECISIONS.md` triggers and fixed entry format
- [x] Add strict `KNOWLEDGE.md` write conditions
- [x] Add strict `WORKLOG.md` append format
- [x] Add 7-day and 30-day review triggers
- [x] Remove fuzzy trigger wording from generated `AGENTS.md`
- [x] Add tests for hardened Codex rules

## Sprint Codex Native Integration

- [x] Reposition Project Copilot as the Codex project memory installer
- [x] Make `project-copilot init` and `project-copilot adopt` the primary setup tools
- [x] Generate Codex-focused `AGENTS.md`
- [x] Generate `docs/CODEX_WORKFLOW.md`
- [x] Update `.ai` memory templates to the final responsibility structure
- [x] Rewrite README and Usage around the Codex-native flow
- [x] Keep interactive mode for compatibility but stop presenting it as the primary flow
- [x] Add tests for Codex native files, README positioning, and `.ai` structure

## Sprint Secretary UX

- [x] Reposition Project Copilot as the project secretary for Codex projects
- [x] Add proposal-driven first-use onboarding
- [x] Add secretary-style project status card
- [x] Add first-impression startup screen focused on identity, status, and next actions
- [x] Hide engineering terms from the startup screen
- [x] Use `项目秘书>` as the interactive prompt
- [x] Add non-interactive Codex environment guidance
- [x] Add Chinese aliases for review, timeline, drift check, decision recording, and roadmap viewing
- [x] Add `.ai/KNOWLEDGE.md`, `.ai/metrics.md`, and `.ai/history/`
- [x] Add rule-based secretary reminders
- [x] Add visual, list-first project review output
- [x] Continue softening OSS wording across secondary workflows

## Sprint Proposal Driven Context

- [x] Replace the default first-run questionnaire with proposal-driven onboarding
- [x] Extract project mission, target users, business goal, MVP scope, stack, stage, roadmap, and decisions from the initial proposal
- [x] Ask follow-up questions only when key information is missing
- [x] Generate `PROJECT_CONTEXT.md`, `STATUS.md`, `ROADMAP.md`, and `DECISIONS.md` from the proposal

## Sprint Evidence Layer Separation

- [x] Add `HYPOTHESES.md` for unconfirmed judgments and low-confidence conclusions
- [x] Restrict `continue` to read-only context recovery without recursive planning
- [x] Route uncertain decision input into `HYPOTHESES.md` instead of `DECISIONS.md`
- [x] Keep `WORKLOG.md` limited to actual completed work, not future planning

## Sprint Memory and Docs Hygiene

- [x] Remove maintenance-only entries from `MEMORY.md`
- [x] Keep `record_decision` out of `MEMORY.md`
- [x] Rephrase documentation around layered memory boundaries
- [x] Normalize `AGENTS.md`, README, Usage, and Codex workflow terminology
- [x] Update the project-state baseline to `pytest -q` passing, 56 passed
- [x] Normalize `.ai/history/` to monthly archive files
- [x] Limit review archives to the recent 3 decisions
- [x] Standardize `timeline_project` into fixed sections

## Sprint Validation

- [x] Start real-project validation with `ai-recruitment`
- [x] Add validation case study template
- [ ] Record daily workflow usage
- [ ] Track project health changes
- [ ] Track Roadmap progress
- [ ] Collect user feedback and pain points
- [ ] Summarize validation findings before adding new capabilities

## v0.4

- [ ] Better project analysis
- [ ] Stronger adopt-project reports
- [ ] Git history analysis
- [ ] More precise project stage detection

## v0.5

- [ ] Release automation
- [ ] Changelog generation
- [ ] Commit message assistance
- [ ] Version bump workflow

## v0.6

- [ ] Optional AI Provider interface
- [ ] Provider configuration design
- [ ] Local-first behavior when no provider is configured

## v1.0

- [ ] Project Secretary for Codex Projects
- [ ] Stable workflow API
- [ ] Stable `.ai` memory format
- [ ] Production-ready CLI UX
