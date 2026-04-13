"""
Command mapping layer: intent + entities -> shell command string(s).

Design:
- **Templates** per intent with placeholders for entities.
- **Platform awareness**: `target_os` selects Unix-style (`rm`) vs Windows
  (`del` / `Remove-Item`) so the same NLU output is usable on both.

The mapper does not execute commands; it only produces strings for review
(or downstream execution with explicit user confirmation).
"""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from typing import List, Optional

from app.nlu import intents as L
from app.nlu.entity_extractor import ExtractedEntities
from app.nlu.pipeline import NLUResult


def _shell_quote(s: str) -> str:
    """Safe single-token quoting for display."""
    return shlex.quote(s)


def _cmd_dquote(s: str) -> str:
    """Double-quote a string for cmd.exe (demo display only)."""
    return '"' + s.replace('"', "").replace("\r", "").replace("\n", "") + '"'


@dataclass
class CommandMappingResult:
    """Outcome of mapping NLU to system commands."""

    command: Optional[str]
    commands: List[str]
    explanation: str
    ambiguous: bool


def _pick_file(e: ExtractedEntities) -> Optional[str]:
    return e.filename or e.path or e.source


def map_command(
    nlu: NLUResult,
    *,
    target_os: Optional[str] = None,
) -> CommandMappingResult:
    """
    Build a command line from classified intent and extracted entities.

    If intent is unknown or entities are missing for a structured intent,
    returns ambiguous=True with explanation text instead of a command.
    """
    os_name = (target_os or os.name).lower()
    is_win = os_name == "nt"
    e = nlu.entities
    intent = nlu.intent

    if intent == L.INTENT_UNKNOWN or nlu.fallback_reason == "low_confidence":
        return CommandMappingResult(
            command=None,
            commands=[],
            explanation=(
                "No command mapped — the phrase did not match a supported action, "
                "or confidence was too low. Try a concrete system task, e.g. "
                "'list all files', 'show running processes', or 'delete file notes.txt'."
            ),
            ambiguous=True,
        )

    if intent == L.INTENT_HELP:
        msg = (
            "Supported: files (delete, copy, move, list, read, mkdir), navigation (cd, pwd), "
            "processes (list, kill), system info, search (grep), find files, ping, environment. "
            "Example: 'list all files', 'grep error in app.log', 'ping google.com'."
        )
        return CommandMappingResult(
            command=None,
            commands=[],
            explanation=msg,
            ambiguous=False,
        )

    if intent == L.INTENT_FILE_DELETE:
        f = _pick_file(e)
        if not f:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Which file should be deleted? Include a name like test.txt.",
                ambiguous=True,
            )
        if is_win:
            cmd = f'del /F /Q {_shell_quote(f)}'
        else:
            cmd = f"rm {_shell_quote(f)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"Remove file {f}",
            ambiguous=False,
        )

    if intent == L.INTENT_FILE_COPY:
        src = e.source or e.filename
        dst = e.destination
        if not src or not dst:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Copy needs source and destination (e.g. copy a.txt to b.txt).",
                ambiguous=True,
            )
        if is_win:
            cmd = f'copy /Y {_shell_quote(src)} {_shell_quote(dst)}'
        else:
            cmd = f"cp {_shell_quote(src)} {_shell_quote(dst)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"Copy {src} -> {dst}",
            ambiguous=False,
        )

    if intent == L.INTENT_FILE_MOVE:
        src = e.source or e.filename
        dst = e.destination or e.path
        if not src or not dst:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Move/rename needs source and destination.",
                ambiguous=True,
            )
        if is_win:
            cmd = f'move /Y {_shell_quote(src)} {_shell_quote(dst)}'
        else:
            cmd = f"mv {_shell_quote(src)} {_shell_quote(dst)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"Move {src} -> {dst}",
            ambiguous=False,
        )

    if intent == L.INTENT_FILE_LIST:
        path = e.path or "."
        if is_win:
            cmd = f'dir {_shell_quote(path)}'
        else:
            cmd = f"ls -la {_shell_quote(path)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"List directory {path}",
            ambiguous=False,
        )

    if intent == L.INTENT_FILE_READ:
        f = _pick_file(e)
        if not f:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Which file to read? Example: read file notes.txt",
                ambiguous=True,
            )
        if is_win:
            cmd = f'type {_shell_quote(f)}'
        else:
            cmd = f"cat {_shell_quote(f)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"Display contents of {f}",
            ambiguous=False,
        )

    if intent == L.INTENT_NAV_CD:
        path = e.path
        if not path:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Which directory? Example: cd /home/user/projects",
                ambiguous=True,
            )
        if is_win:
            cmd = f"cd /d {_shell_quote(path)}"
        else:
            cmd = f"cd {_shell_quote(path)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"Change directory to {path}",
            ambiguous=False,
        )

    if intent == L.INTENT_NAV_PWD:
        if is_win:
            return CommandMappingResult(
                command="echo %CD%",
                commands=["echo %CD%"],
                explanation="Print current directory (cmd.exe). In PowerShell use Get-Location.",
                ambiguous=False,
            )
        return CommandMappingResult(
            command="pwd",
            commands=["pwd"],
            explanation="Print working directory",
            ambiguous=False,
        )

    if intent == L.INTENT_PROC_LIST:
        if is_win:
            cmd = "tasklist"
        else:
            cmd = "ps aux"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation="List processes",
            ambiguous=False,
        )

    if intent == L.INTENT_PROC_KILL:
        if e.pid is not None:
            if is_win:
                cmd = f"taskkill /PID {e.pid} /F"
            else:
                cmd = f"kill {_shell_quote(str(e.pid))}"
            return CommandMappingResult(
                command=cmd,
                commands=[cmd],
                explanation=f"Terminate PID {e.pid}",
                ambiguous=False,
            )
        name = e.process_name
        if name:
            if is_win:
                cmd = f'taskkill /IM {_shell_quote(name)} /F'
            else:
                cmd = f"pkill -f {_shell_quote(name)}"
            return CommandMappingResult(
                command=cmd,
                commands=[cmd],
                explanation=f"Terminate process matching {name}",
                ambiguous=False,
            )
        return CommandMappingResult(
            command=None,
            commands=[],
            explanation="Specify a PID (e.g. kill process 1234) or process name.",
            ambiguous=True,
        )

    if intent == L.INTENT_SYSTEM_INFO:
        if is_win:
            cmds = ["systeminfo", "wmic logicaldisk get size,freespace,caption"]
            return CommandMappingResult(
                command=cmds[0],
                commands=cmds,
                explanation="System and disk information (Windows)",
                ambiguous=False,
            )
        cmds = ["uname -a", "df -h", "free -h"]
        return CommandMappingResult(
            command=" && ".join(cmds),
            commands=cmds,
            explanation="System, disk, and memory information (Unix)",
            ambiguous=False,
        )

    if intent == L.INTENT_FILE_MKDIR:
        path = e.path
        if not path:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Say where to create the folder, e.g. 'create folder build' or 'mkdir dist'.",
                ambiguous=True,
            )
        if is_win:
            cmd = f"mkdir {_shell_quote(path)}"
        else:
            cmd = f"mkdir -p {_shell_quote(path)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"Create directory {path}",
            ambiguous=False,
        )

    if intent == L.INTENT_SEARCH_GREP:
        pat = e.pattern
        fn = e.filename
        if not pat:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Specify text to search, e.g. 'grep ERROR in server.log'.",
                ambiguous=True,
            )
        if is_win:
            if fn:
                cmd = f"findstr /N /I /C:{_cmd_dquote(pat)} {_cmd_dquote(fn)}"
            else:
                cmd = f"findstr /S /N /I /C:{_cmd_dquote(pat)} *.*"
        else:
            if fn:
                cmd = f"grep -n {_shell_quote(pat)} {_shell_quote(fn)}"
            else:
                cmd = f"grep -rn {_shell_quote(pat)} ."
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation="Search for a text pattern in files",
            ambiguous=False,
        )

    if intent == L.INTENT_FIND_FILES:
        pat = e.pattern or "*"
        if is_win:
            cmd = f"dir /s /b {_shell_quote(pat)}"
        else:
            qpat = pat if "*" in pat or "?" in pat else f"*{pat}*"
            cmd = f"find . -name {_shell_quote(qpat)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"Find files matching {pat}",
            ambiguous=False,
        )

    if intent == L.INTENT_NET_PING:
        host = e.host
        if not host:
            return CommandMappingResult(
                command=None,
                commands=[],
                explanation="Which host to ping? Example: 'ping google.com'.",
                ambiguous=True,
            )
        if is_win:
            cmd = f"ping {_shell_quote(host)}"
        else:
            cmd = f"ping -c 4 {_shell_quote(host)}"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation=f"ICMP ping to {host}",
            ambiguous=False,
        )

    if intent == L.INTENT_ENV_SHOW:
        if is_win:
            cmd = "set"
        else:
            cmd = "printenv | sort | head -80"
        return CommandMappingResult(
            command=cmd,
            commands=[cmd],
            explanation="Show environment variables (truncated on Unix)",
            ambiguous=False,
        )

    return CommandMappingResult(
        command=None,
        commands=[],
        explanation="No mapper for this intent.",
        ambiguous=True,
    )
