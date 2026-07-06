---
name: cloud-aws-governance
description: Use this skill when writing or reviewing code that inspects AWS infrastructure (EC2, S3, IAM, RDS, Lambda) from within an agent workflow. Wraps read-only boto3 lookups behind a required correlation id so every call is audit-logged and traceable back to the invoking run.
metadata:
  origin: ECC
---

# Cloud AWS Governance Skill

Patterns for adding read-only, audit-logged AWS infrastructure inspection to an
agent workflow, without embedding untracked boto3 calls scattered across
the codebase.

## When to Activate

- Adding a tool/function that inspects live AWS resources (EC2, S3, IAM, RDS, Lambda)
- Reviewing code that calls boto3 directly without an audit trail
- Wiring cloud inspection into a multi-step or multi-agent workflow that needs
  every external call traceable to a single run/session id

## How It Works

- Every inspection call must be constructed with a `correlation_id` — a
  stable identifier for the current run/session — so all AWS lookups in
  that run share one traceable thread in logs.
- Before performing any AWS API call, emit a structured log line prefixed
  `[ECC AWS GOVERNANCE] [Correlation ID: <id>]` describing the action about
  to run.
- Wrap the actual boto3 call in `try/except` around `ClientError` /
  `BotoCoreError` (and a final catch-all), logging failures with the same
  correlation id instead of letting exceptions propagate silently.
- Keep all mapped operations read-only (`describe_*` / `list_*`) — this
  pattern is for inspection, not mutation.
- Reference implementation: [`aws_utilities.py`](aws_utilities.py)
  (`AWSGovernanceBridge.inspect_infrastructure`). Tool-calling metadata for
  agents is defined in [`tool_schema.json`](tool_schema.json), which marks
  `correlation_id` as a required parameter sourced from the caller's
  session/run context.

## Examples

```python
bridge = AWSGovernanceBridge(correlation_id=run_id)
result = bridge.inspect_infrastructure("ec2_instances")
# result["status"] is "success" or "error"; both carry correlation_id
```

## Notes

- This module lives outside the Node.js/CommonJS convention used
  elsewhere in this repo's `scripts/` — it is Python because it targets a
  Python/LangGraph execution surface. If this skill is consumed by a
  Node-based hook or command in this repo, treat `aws_utilities.py` as
  reference material to port, not as directly importable code.
- No credentials are accepted, stored, or logged by this module — it
  relies on the ambient boto3/AWS credential chain.
