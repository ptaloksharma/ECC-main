"""Core Framework Extensions.

New convention, established 2026-07-06: `core/` previously held only
`orchestrator_factory.py` with no subdirectory pattern for platform-wide,
cross-cutting capabilities. Modules placed here are shared by any ECC
agent module (not domain-specific), keyed by `core.orchestrator_factory.
GovernanceContext.correlation_id` so they stay joined to the same
telemetry trail as the orchestrator layer.
"""
