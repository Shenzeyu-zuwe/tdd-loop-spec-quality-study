# -*- coding: utf-8 -*-
"""
Agent session — inner loop, one Claude Code CLI subprocess invocation.

The Claude CLI brings its own tool suite (Read/Edit/Write/Grep/Glob/Bash),
automatically loads CLAUDE.md, and handles its own tool-calling loop. The
framework only supplies: system prompt, user message, model name, cwd,
tool/permission flags, and timeout policy.
"""

import json
import logging
import subprocess
import time
from pathlib import Path

logger = logging.getLogger("tdd_loop.agent")

# Hard timeout for a single CLI invocation. Bounds runaway / hung subprocesses.
CLI_SESSION_TIMEOUT = 900  # 15 min


def run_agent_session(
    client,
    model: str,
    system_prompt: str,
    user_message: str,
    project_dir: Path,
    use_tools: bool = True,
    json_mode: bool = False,
    max_turns: int | None = None,
    resume_header: str = "",
    **kwargs,
) -> tuple[str, str, dict]:
    """Run a single Claude Code CLI session.

    Returns:
        (status, response_text, meta)
        status: "ok" | "error"
        meta: {"session_id", "cost_usd", "duration_ms", "num_turns"}
    """
    return _run_claude_cli_session(
        model=model,
        system_prompt=system_prompt,
        user_message=user_message,
        project_dir=project_dir,
        use_tools=use_tools,
        json_mode=json_mode,
        max_turns=max_turns,
        resume_header=resume_header,
    )


def _run_claude_cli_session(
    model: str,
    system_prompt: str,
    user_message: str,
    project_dir: Path,
    use_tools: bool = True,
    json_mode: bool = False,
    max_turns: int | None = None,
    resume_header: str = "",
) -> tuple[str, str, dict]:
    empty_meta = {"session_id": None, "cost_usd": 0, "duration_ms": 0, "num_turns": 0}

    if resume_header:
        prompt = f"{resume_header}\n\n---\n\n{system_prompt}\n\n---\n\n{user_message}"
    else:
        prompt = f"{system_prompt}\n\n---\n\n{user_message}"

    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if model and model != "default":
        cmd.extend(["--model", model])
    cmd.extend(["--tools", "default", "--permission-mode", "bypassPermissions"])
    if max_turns is None:
        max_turns = 30
    cmd.extend(["--max-turns", str(max_turns)])

    role = "Tester" if json_mode else "Worker"
    logger.info(f"  Claude CLI start: role={role}, model={model}, prompt_chars={len(prompt)}")

    t0 = time.time()
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
        )

        while True:
            try:
                proc.wait(timeout=30)
                break
            except subprocess.TimeoutExpired:
                elapsed = time.time() - t0
                m, s = divmod(int(elapsed), 60)
                logger.info(f"  ⏳ {role} running... ({m}m{s}s)")
                if elapsed > CLI_SESSION_TIMEOUT:
                    logger.error(f"  ✗ {role} hard timeout ({CLI_SESSION_TIMEOUT}s), killing")
                    proc.kill()
                    proc.wait(timeout=10)
                    return "error", f"CLI hard timeout ({CLI_SESSION_TIMEOUT}s)", empty_meta

        elapsed = time.time() - t0
        stdout = proc.stdout.read() if proc.stdout else ""
        stderr = proc.stderr.read() if proc.stderr else ""
        m, s = divmod(int(elapsed), 60)

        if proc.returncode != 0:
            logger.error(f"  ✗ {role} failed (exit={proc.returncode}, {m}m{s}s)")
            logger.error(f"    stderr: {(stderr or '').strip()[:500] or '(empty)'}")
            meta = _extract_session_meta(stdout)
            return "error", (stderr or stdout or "")[:500], meta

        meta = _extract_session_meta(stdout)
        sid = (meta.get("session_id") or "?")[:8]
        cost = meta.get("cost_usd", 0)
        logger.info(f"  ✓ {role} done ({m}m{s}s, session={sid}…, ${cost:.4f})")

        output_text = _parse_claude_cli_output(stdout)
        return "ok", output_text, meta

    except FileNotFoundError:
        logger.error("  'claude' not found. Install: npm install -g @anthropic-ai/claude-code")
        return "error", "claude CLI not found", empty_meta
    except Exception as e:
        logger.error(f"  ✗ {role} exception: {e}")
        return "error", str(e), empty_meta


def _extract_session_meta(stdout: str) -> dict:
    meta = {"session_id": None, "cost_usd": 0, "duration_ms": 0, "num_turns": 0}
    if not stdout.strip():
        return meta
    try:
        data = json.loads(stdout)
        if isinstance(data, dict):
            meta["session_id"] = data.get("session_id")
            meta["cost_usd"] = data.get("total_cost_usd", 0)
            meta["duration_ms"] = data.get("duration_ms", 0)
            meta["num_turns"] = data.get("num_turns", 0)
    except json.JSONDecodeError:
        for line in reversed(stdout.strip().split("\n")):
            try:
                data = json.loads(line.strip())
                if isinstance(data, dict) and "session_id" in data:
                    meta["session_id"] = data.get("session_id")
                    meta["cost_usd"] = data.get("total_cost_usd", 0)
                    meta["duration_ms"] = data.get("duration_ms", 0)
                    meta["num_turns"] = data.get("num_turns", 0)
                    break
            except json.JSONDecodeError:
                continue
    return meta


def _parse_claude_cli_output(stdout: str) -> str:
    if not stdout.strip():
        return ""
    try:
        data = json.loads(stdout)
        if isinstance(data, dict):
            return data.get("result", data.get("text", stdout))
        return stdout
    except json.JSONDecodeError:
        for line in reversed(stdout.strip().split("\n")):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict) and "result" in data:
                    return data["result"]
            except json.JSONDecodeError:
                continue
        return stdout
