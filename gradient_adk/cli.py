"""Command-line interface for Gradient ADK."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

from .server import run_server

STARTER_AGENT_TEMPLATE = (
    "from gradient_adk import entrypoint\n\n"
    "@entrypoint\n"
    "def entry(payload, context):\n"
    "    return {'echo': payload}\n"
)


def _load_callable(target: str) -> Callable[[dict[str, Any], dict[str, Any]], Any]:
    if ":" not in target:
        raise ValueError("Target must use module:function format")

    module_name, function_name = target.split(":", maxsplit=1)
    module = importlib.import_module(module_name)

    try:
        func = getattr(module, function_name)
    except AttributeError as exc:
        raise ValueError(f"Function '{function_name}' not found in module '{module_name}'") from exc

    if not callable(func):
        raise ValueError(f"Target '{target}' is not callable")

    return func


def _cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.path) / "agent.py"
    if target.exists():
        print(f"File already exists: {target}", file=sys.stderr)
        return 1

    target.write_text(STARTER_AGENT_TEMPLATE, encoding="utf-8")
    print(f"Created starter agent at {target}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    entry_func = _load_callable(args.module)
    run_server(entry_func, host=args.host, port=args.port)
    return 0


def _cmd_placeholder(name: str) -> Callable[[argparse.Namespace], int]:
    def run(_: argparse.Namespace) -> int:
        print(f"'{name}' command scaffolded; implementation pending.")
        return 0

    return run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gradient")
    subparsers = parser.add_subparsers(dest="resource", required=True)

    agent = subparsers.add_parser("agent")
    agent_sub = agent.add_subparsers(dest="command", required=True)

    init_cmd = agent_sub.add_parser("init")
    init_cmd.add_argument("path", nargs="?", default=".")
    init_cmd.set_defaults(handler=_cmd_init)

    run_cmd = agent_sub.add_parser("run")
    run_cmd.add_argument("--module", default="agent:entry")
    run_cmd.add_argument("--host", default="0.0.0.0")
    run_cmd.add_argument("--port", type=int, default=8080)
    run_cmd.set_defaults(handler=_cmd_run)

    for name in ("deploy", "configure", "traces", "logs"):
        cmd = agent_sub.add_parser(name)
        cmd.set_defaults(handler=_cmd_placeholder(name))

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
