"""Command-line interface for Gradient ADK."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

from .client import GradientAPIError, GradientClient
from .config import ENV_API_KEY, get_api_key, load_config, save_config
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


def _print_no_key_error() -> None:
    print(
        f"Error: Model Access Key not set.\n"
        f"  Option 1 (environment variable): export {ENV_API_KEY}=<your-key>\n"
        f"  Option 2 (config file):          gradient agent configure --api-key <your-key>",
        file=sys.stderr,
    )


def _require_api_key(config: dict[str, Any]) -> str | None:
    """Return the API key or print an error and return None."""
    key = get_api_key(config)
    if not key:
        _print_no_key_error()
    return key


# ------------------------------------------------------------------
# Command implementations
# ------------------------------------------------------------------


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


def _cmd_configure(args: argparse.Namespace) -> int:
    """Persist API key and optional settings to ~/.gradient/config.json."""
    config = load_config()
    changed = False

    if args.api_key:
        config["api_key"] = args.api_key
        changed = True

    if args.agent_id:
        config["agent_id"] = args.agent_id
        changed = True

    if args.api_base:
        config["api_base"] = args.api_base
        changed = True

    if changed:
        save_config(config)
        print("Configuration saved.")
        if args.api_key:
            print("  api_key  : ****")  # never echo the actual key
        if args.agent_id:
            print(f"  agent_id : {args.agent_id}")
        if args.api_base:
            print(f"  api_base : {args.api_base}")
    else:
        # No flags — display the current configuration (mask the key).
        if not config:
            print("No configuration found. Use --api-key, --agent-id, or --api-base to set values.")
        else:
            display = dict(config)
            if "api_key" in display:
                k = display["api_key"]
                display["api_key"] = k[:4] + "****" if len(k) > 4 else "****"
            print(json.dumps(display, indent=2))

    return 0


def _cmd_deploy(args: argparse.Namespace) -> int:
    """Deploy the agent to the Gradient platform."""
    config = load_config()
    api_key = _require_api_key(config)
    if not api_key:
        return 1

    # Validate that the target module:function is importable before deploying.
    try:
        _load_callable(args.module)
    except (ValueError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    api_base = args.api_base or config.get("api_base")
    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if api_base:
        client_kwargs["api_base"] = api_base

    client = GradientClient(**client_kwargs)

    print(f"Deploying agent '{args.name}' (module={args.module}, region={args.region}) …")
    try:
        result = client.deploy_agent(
            name=args.name,
            module=args.module,
            region=args.region,
        )
    except GradientAPIError as exc:
        print(f"Deploy failed: {exc}", file=sys.stderr)
        return 1

    agent_id = result.get("agent_id") or result.get("id")
    status = result.get("status", "unknown")
    print(f"Deploy succeeded. Status: {status}")
    if agent_id:
        print(f"Agent ID: {agent_id}")
        # Persist agent_id so traces/logs commands can pick it up automatically.
        config["agent_id"] = agent_id
        save_config(config)
        print(f"Agent ID saved to config for use with 'traces' and 'logs'.")

    return 0


def _cmd_traces(args: argparse.Namespace) -> int:
    """Fetch and display trace events for a deployed agent."""
    config = load_config()
    api_key = _require_api_key(config)
    if not api_key:
        return 1

    agent_id = args.agent_id or config.get("agent_id")
    if not agent_id:
        print(
            "Error: Agent ID not set. Use --agent-id or run 'gradient agent configure --agent-id <ID>'.",
            file=sys.stderr,
        )
        return 1

    api_base = args.api_base or config.get("api_base")
    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if api_base:
        client_kwargs["api_base"] = api_base

    client = GradientClient(**client_kwargs)

    try:
        traces = client.get_traces(agent_id, limit=args.limit)
    except GradientAPIError as exc:
        print(f"Failed to fetch traces: {exc}", file=sys.stderr)
        return 1

    if not traces:
        print("No traces found.")
        return 0

    for event in traces:
        print(json.dumps(event))

    return 0


def _cmd_logs(args: argparse.Namespace) -> int:
    """Fetch and display log lines for a deployed agent."""
    config = load_config()
    api_key = _require_api_key(config)
    if not api_key:
        return 1

    agent_id = args.agent_id or config.get("agent_id")
    if not agent_id:
        print(
            "Error: Agent ID not set. Use --agent-id or run 'gradient agent configure --agent-id <ID>'.",
            file=sys.stderr,
        )
        return 1

    api_base = args.api_base or config.get("api_base")
    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if api_base:
        client_kwargs["api_base"] = api_base

    client = GradientClient(**client_kwargs)

    if args.follow:
        _stream_logs(client, agent_id, args.limit)
        return 0

    try:
        lines = client.get_logs(agent_id, limit=args.limit)
    except GradientAPIError as exc:
        print(f"Failed to fetch logs: {exc}", file=sys.stderr)
        return 1

    if not lines:
        print("No logs found.")
        return 0

    for line in lines:
        ts = line.get("timestamp", "")
        msg = line.get("message") or json.dumps(line)
        print(f"{ts}  {msg}" if ts else msg)

    return 0


def _stream_logs(client: GradientClient, agent_id: str, limit: int) -> None:
    """Continuously poll for new log lines (Ctrl-C to stop)."""
    print("Streaming logs… (press Ctrl-C to stop)")
    seen: set[str] = set()
    try:
        while True:
            try:
                lines = client.get_logs(agent_id, limit=limit)
            except GradientAPIError as exc:
                print(f"Warning: {exc}", file=sys.stderr)
                time.sleep(5)
                continue

            for line in lines:
                key = line.get("id") or json.dumps(line)
                if key not in seen:
                    seen.add(key)
                    ts = line.get("timestamp", "")
                    msg = line.get("message") or json.dumps(line)
                    print(f"{ts}  {msg}" if ts else msg)

            time.sleep(3)
    except KeyboardInterrupt:
        pass


# ------------------------------------------------------------------
# Argument parser
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gradient")
    subparsers = parser.add_subparsers(dest="resource", required=True)

    agent = subparsers.add_parser("agent")
    agent_sub = agent.add_subparsers(dest="command", required=True)

    # --- init ---
    init_cmd = agent_sub.add_parser("init")
    init_cmd.add_argument("path", nargs="?", default=".")
    init_cmd.set_defaults(handler=_cmd_init)

    # --- run ---
    run_cmd = agent_sub.add_parser("run")
    run_cmd.add_argument("--module", default="agent:entry")
    run_cmd.add_argument("--host", default="0.0.0.0")
    run_cmd.add_argument("--port", type=int, default=8080)
    run_cmd.set_defaults(handler=_cmd_run)

    # --- configure ---
    configure_cmd = agent_sub.add_parser("configure")
    configure_cmd.add_argument("--api-key", dest="api_key", default=None)
    configure_cmd.add_argument("--agent-id", dest="agent_id", default=None)
    configure_cmd.add_argument("--api-base", dest="api_base", default=None)
    configure_cmd.set_defaults(handler=_cmd_configure)

    # --- deploy ---
    deploy_cmd = agent_sub.add_parser("deploy")
    deploy_cmd.add_argument("--module", default="agent:entry")
    deploy_cmd.add_argument("--name", default="my-agent")
    deploy_cmd.add_argument("--region", default="nyc3")
    deploy_cmd.add_argument("--api-base", dest="api_base", default=None)
    deploy_cmd.set_defaults(handler=_cmd_deploy)

    # --- traces ---
    traces_cmd = agent_sub.add_parser("traces")
    traces_cmd.add_argument("--agent-id", dest="agent_id", default=None)
    traces_cmd.add_argument("--limit", type=int, default=20)
    traces_cmd.add_argument("--api-base", dest="api_base", default=None)
    traces_cmd.set_defaults(handler=_cmd_traces)

    # --- logs ---
    logs_cmd = agent_sub.add_parser("logs")
    logs_cmd.add_argument("--agent-id", dest="agent_id", default=None)
    logs_cmd.add_argument("--limit", type=int, default=100)
    logs_cmd.add_argument("--follow", action="store_true")
    logs_cmd.add_argument("--api-base", dest="api_base", default=None)
    logs_cmd.set_defaults(handler=_cmd_logs)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
