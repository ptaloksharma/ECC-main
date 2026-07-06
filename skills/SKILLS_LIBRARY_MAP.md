# Skills Roadmap — Meta-Cognition / Governance / Infra / Collaboration

Working roadmap for a set of skills grouped around four themes. This is a
**proposal to reconcile against a real source-of-truth spec if one
exists** — no such spec was found in this repository as of 2026-07-03,
so nothing below should be read as "already aligned to history."

Skills in this repo are flat: `skills/<kebab-case-name>/SKILL.md` with
YAML frontmatter (`name`, `description`, `metadata`), following the
pattern documented in the repo's `CLAUDE.md` and used by all 277
existing skills (e.g. `skills/react-patterns/`, `skills/security-review/`).
There is no pillar/sub-folder nesting anywhere else in `skills/` — the
four themes below are **tags for grouping in this document only**, not
physical directories.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Implemented (`SKILL.md` present, follows repo convention)

---

## Theme: Meta-Cognition

Reasoning, self-learning loops, exception management, automatic skill discovery.

- [ ] Self-reflection / post-run critique
- [ ] Self-learning pattern extraction (see existing `continuous-learning`, `continuous-learning-v2` — check for overlap before adding new)
- [ ] Exception handling / failure classification
- [ ] Automatic skill discovery / routing heuristics (see existing `skill-scout`, `skill-comply`, `skill-stocktake` — check for overlap before adding new)

## Theme: Operational Intelligence & Infrastructure

AWS/cloud utility modules, local infra emulation, schema parsing, execution routing.

- [x] `cloud-aws-governance` — read-only, audit-logged AWS inspection (EC2/S3/IAM/RDS/Lambda). See [`skills/cloud-aws-governance/SKILL.md`](cloud-aws-governance/SKILL.md); reference implementation in `aws_utilities.py`, tool metadata in `tool_schema.json`.
- [ ] LocalStack-based local AWS emulation for testing the above without live credentials
- [ ] Generic cloud tool-schema parsing/validation
- [ ] Execution routing across infra tools

## Theme: Governance & Telemetry

Security, multi-tenant compliance, audit trails, token/context boundaries, safety guardrails.

- [ ] Correlation id propagation as a documented convention (currently ad hoc, only exercised by `cloud-aws-governance`)
- [ ] Audit log emitter pattern (currently only `[ECC AWS GOVERNANCE]`-prefixed prints in `cloud-aws-governance`; not a shared utility)
- [ ] Multi-tenant compliance checks — **no implementation exists yet; flagging explicitly so this isn't assumed done**
- [ ] Token/context boundary enforcement (see existing `context-budget`, `token-budget-advisor` — check for overlap before adding new)
- [ ] Safety guardrails (see existing `safety-guard` — check for overlap before adding new)

## Theme: Collaboration & Execution

Multi-agent synchronization, inter-agent handoffs, state tracking, task decomposition.

- [ ] Multi-agent handoff pattern (see existing `team-agent-orchestration`, `orch-pipeline` — check for overlap before adding new)
- [ ] State tracking across agent runs
- [ ] Task decomposition pattern (see existing `plan-orchestrate` — check for overlap before adding new)

---

## Open Items

- **No "52-skill" or "4-pillar" historical spec has been located in this
  repository.** If one exists outside this repo, share it directly and
  this document will be rewritten to match it exactly — including real
  names in place of the above.
- Several themes overlap with skills that already exist in this library
  (noted inline above). Before building anything new, check those first
  to avoid duplicating coverage.
- `core/orchestrator_factory.py` (Python, outside `skills/`) and
  `skills/cloud-aws-governance/` (Python) both sit outside this repo's
  documented architecture, which is Node.js/CommonJS for `scripts/` and
  Markdown for `skills/` (see `CLAUDE.md`). They're kept as-is since they
  target a separate Python/LangGraph execution surface, but that's a
  deliberate exception, not the norm — don't use them as a template for
  future skills in this repo.
