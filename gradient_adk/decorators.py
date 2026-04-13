"""Decorators for registering and tracing ADK entrypoints."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

_ENTRYPOINT: Optional[Callable[..., Any]] = None


def get_entrypoint() -> Optional[Callable[..., Any]]:
    return _ENTRYPOINT


def entrypoint(func: F) -> F:
    global _ENTRYPOINT
    _ENTRYPOINT = func
    setattr(func, "__gradient_entrypoint__", True)
    return func


def _extract_context(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    if "context" in kwargs:
        return kwargs["context"]
    if len(args) > 1:
        return args[1]
    return None


def _trace(kind: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            context = _extract_context(args, kwargs)
            if isinstance(context, dict):
                context.setdefault("trace_events", []).append(
                    {"type": kind, "name": func.__name__}
                )
            return func(*args, **kwargs)

        setattr(wrapper, "__gradient_trace_type__", kind)
        return wrapper  # type: ignore[return-value]

    return decorator


trace_llm = _trace("llm")
trace_tool = _trace("tool")
trace_retriever = _trace("retriever")
