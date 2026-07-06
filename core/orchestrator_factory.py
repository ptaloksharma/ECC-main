"""Pluggable orchestrator factory for ECC Phase 2.5.

Provides a common execution contract so different agent frameworks
(LangGraph, CrewAI, sequential routers, ...) can be swapped behind a
single interface while sharing one telemetry correlation id.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Type


class GovernanceContext:
    """Carries a unique correlation id and shared metadata across an
    orchestrator invocation, so telemetry stays joined regardless of
    which underlying framework executed the request.
    """

    def __init__(
        self,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.correlation_id: str = correlation_id or str(uuid.uuid4())
        self.metadata: Dict[str, Any] = metadata or {}

    def with_metadata(self, **updates: Any) -> "GovernanceContext":
        """Return a new context sharing the same correlation id but with
        merged metadata, so sub-steps can annotate context without
        splitting the telemetry trail.
        """
        merged = {**self.metadata, **updates}
        return GovernanceContext(correlation_id=self.correlation_id, metadata=merged)

    def __repr__(self) -> str:
        return f"GovernanceContext(correlation_id={self.correlation_id!r}, metadata={self.metadata!r})"


class BaseOrchestrator(ABC):
    """Interface contract every orchestration engine wrapper must satisfy."""

    @abstractmethod
    def execute(self, prompt: str, context: GovernanceContext) -> Any:
        """Run `prompt` through the underlying engine using `context` for
        telemetry/config propagation, and return the engine's result.
        """
        raise NotImplementedError


class LangGraphOrchestrator(BaseOrchestrator):
    """Wraps a LangGraph-compiled graph so its thread/run config carries
    the GovernanceContext's correlation id, keeping LangGraph's own
    checkpointing/tracing joined to ECC telemetry.
    """

    def __init__(self, graph: Any) -> None:
        """`graph` is an object exposing `.invoke(input, config=...)`,
        matching a compiled LangGraph graph (e.g. `StateGraph.compile()`).
        """
        self._graph = graph

    def execute(self, prompt: str, context: GovernanceContext) -> Any:
        config = {
            "configurable": {
                "thread_id": context.correlation_id,
            },
            "metadata": {
                "correlation_id": context.correlation_id,
                **context.metadata,
            },
        }
        return self._graph.invoke({"input": prompt}, config=config)


class AlternativeOrchestrator(BaseOrchestrator):
    """Blueprint wrapper for a secondary engine (e.g. a sequential router
    or CrewAI crew) that consumes the same prompt and GovernanceContext
    without splitting telemetry into a separate identifier.
    """

    def __init__(self, engine: Callable[[str, Dict[str, Any]], Any]) -> None:
        """`engine` is any callable accepting `(prompt, run_metadata)`,
        matching e.g. a CrewAI `Crew.kickoff` shim or a plain sequential
        router function.
        """
        self._engine = engine

    def execute(self, prompt: str, context: GovernanceContext) -> Any:
        run_metadata = {
            "correlation_id": context.correlation_id,
            **context.metadata,
        }
        return self._engine(prompt, run_metadata)


class OrchestratorFactory:
    """Registry for orchestrator engines, keyed by name, so callers can
    register new engines and fetch instances without hard-coding
    framework-specific construction logic elsewhere.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Type[BaseOrchestrator]] = {}

    def register(self, name: str, orchestrator_cls: Type[BaseOrchestrator]) -> None:
        if not issubclass(orchestrator_cls, BaseOrchestrator):
            raise TypeError(f"{orchestrator_cls!r} must subclass BaseOrchestrator")
        self._registry[name] = orchestrator_cls

    def create(self, name: str, *args: Any, **kwargs: Any) -> BaseOrchestrator:
        try:
            orchestrator_cls = self._registry[name]
        except KeyError as exc:
            raise KeyError(
                f"No orchestrator registered under {name!r}. "
                f"Known engines: {sorted(self._registry)}"
            ) from exc
        return orchestrator_cls(*args, **kwargs)

    def available(self) -> Dict[str, Type[BaseOrchestrator]]:
        return dict(self._registry)


DEFAULT_FACTORY = OrchestratorFactory()
DEFAULT_FACTORY.register("langgraph", LangGraphOrchestrator)
DEFAULT_FACTORY.register("alternative", AlternativeOrchestrator)
