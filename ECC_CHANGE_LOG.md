# ECC Change Log

## Phase 2.5 — Pluggable Orchestration Foundation

- **Date**: 2026-07-03
- **File**: `core/orchestrator_factory.py`
- **Status**: Initialized

Introduced the core pluggable orchestration foundation for Phase 2.5:

- `GovernanceContext` — carries a UUID `correlation_id` plus shared metadata so telemetry stays joined across framework boundaries.
- `BaseOrchestrator` — abstract interface contract (`execute(prompt, context)`) all engine wrappers must implement.
- `LangGraphOrchestrator` — concrete wrapper that threads `GovernanceContext` into a LangGraph run/thread config.
- `AlternativeOrchestrator` — secondary blueprint wrapper (sequential router / CrewAI-style) consuming the same prompt and context without splitting telemetry.
- `OrchestratorFactory` — registry for registering and dynamically fetching orchestrator engines by name.

Syntax verified via `py_compile`.

## Phase 2.5 — Governed AWS Cloud Skills Layer

- **Date**: 2026-07-03
- **Files**: `skills/cloud_aws/aws_utilities.py`, `skills/cloud_aws/tool_schema.json`
- **Status**: Deployed

Introduced the governed AWS cloud skills layer, wired into the Phase 2.5 governance model:

- `AWSGovernanceBridge` — requires a `correlation_id` (sourced from `GovernanceContext`) at construction; every action is prefixed with an `[ECC AWS GOVERNANCE] [Correlation ID: ...]` audit log line.
- `inspect_infrastructure(resource_type)` — read-only boto3-backed lookup (EC2, S3, IAM, RDS, Lambda) with try/except handling around `ClientError`/`BotoCoreError` and unexpected exceptions, all logged with the correlation id for full telemetry traceability.
- `tool_schema.json` — tool metadata specification instructing any invoking LLM agent that `correlation_id` from the active `GovernanceContext` is a required parameter, plus a documented read-only/least-privilege security model.

Syntax and schema verified via `py_compile` and `json.load`.

## Phase 2.5 — 52-Skill Library Pillar Scaffold

- **Date**: 2026-07-03
- **Dirs**: `skills/meta_cognitive/`, `skills/governance_telemetry/`, `skills/infrastructure_cloud/`, `skills/collaboration_execution/`
- **File**: `skills/SKILLS_LIBRARY_MAP.md`
- **Status**: Deployed (scaffold)

Deployed the 4 pillar folders for the 52-skill framework and added
`skills/SKILLS_LIBRARY_MAP.md`, a checklist manifest of 13 placeholder
skill slots per pillar (meta-cognitive, governance/telemetry,
infrastructure/cloud, collaboration/execution). Placeholder names are
scaffold-only pending reconciliation against the actual historical
design spec, which is not yet present in this repo.

## Phase 2.5 — AWS Skill Relocated Under Infrastructure Pillar

- **Date**: 2026-07-03
- **Change**: Moved `skills/cloud_aws/` → `skills/infrastructure_cloud/cloud_aws/`
- **Status**: Complete

Relocated the AWS governance bridge module (`aws_utilities.py`,
`tool_schema.json`) into `skills/infrastructure_cloud/` so cloud
capabilities sit under their pillar directory. Updated the `module`
path inside `tool_schema.json` and the references in
`skills/SKILLS_LIBRARY_MAP.md` accordingly; resolved the open
"merge vs. standalone" item from the prior scaffold entry in favor of
merging. Re-verified via `py_compile` and `json.load` post-move.

## Phase 2.5 — Reconciled Against Actual Skill Format (Correction)

- **Date**: 2026-07-03
- **Change**: Flattened `skills/infrastructure_cloud/cloud_aws/` → `skills/cloud-aws-governance/`; removed the empty `skills/meta_cognitive/`, `skills/governance_telemetry/`, `skills/infrastructure_cloud/`, `skills/collaboration_execution/` pillar folders; rewrote `skills/SKILLS_LIBRARY_MAP.md`.
- **Status**: Complete
- **Reason**: user-confirmed correction, see note below.

Two prior entries in this log (the "52-skill pillar scaffold" and the
"AWS skill relocated under infrastructure pillar" entries above)
described a directory structure — nested Python "pillar" folders under
`skills/` — that does not match this repository's actual, established
skill format. All 277 pre-existing skills in `skills/` are flat
`skills/<kebab-case-name>/SKILL.md` directories with YAML frontmatter,
per this repo's own `CLAUDE.md`. The nested pillar structure was
scaffolded against a "historical design spec" that could not be located
anywhere in this repository across three separate checks this session.

Correction applied:
- `skills/cloud-aws-governance/` is now a real, conforming skill: it has
  a `SKILL.md` (When to Activate / How It Works / Examples), with
  `aws_utilities.py` and `tool_schema.json` kept alongside as reference
  implementation and tool metadata.
- The four empty pillar folders were removed (they were created this
  session and contained no other files).
- `skills/SKILLS_LIBRARY_MAP.md` was rewritten as an explicitly-labeled
  roadmap/proposal — it groups planned skills by theme for readability
  only (no physical pillar folders) and states plainly that no source
  spec has been found, rather than asserting spec alignment.

`core/orchestrator_factory.py` remains Python outside the Node.js
convention used elsewhere in this repo, by design, per the prior
confirmation that it targets a separate LangGraph/Python execution
surface — flagging here for visibility, not changing it.
