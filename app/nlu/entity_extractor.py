"""
Entity extraction using regex and light heuristics (no NER model required).

Extracts:
- **path**: quoted paths or obvious slash-separated segments
- **filename**: tokens that look like file.ext
- **pid**: numeric process ids
- **source** / **dest**: for copy/move patterns

For production, consider spaCy NER, regex + gazetteers, or a seq2seq slot filler.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExtractedEntities:
    """Structured slots from user text."""

    path: Optional[str] = None
    filename: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    pid: Optional[int] = None
    process_name: Optional[str] = None
    # ping host, grep/find pattern, mkdir target
    host: Optional[str] = None
    pattern: Optional[str] = None
    raw_tokens: List[str] = field(default_factory=list)


# Quoted strings
_QUOTED = re.compile(r'["\']([^"\']+)["\']')
# path-like: /foo/bar or C:\foo or .\rel
_PATHLIKE = re.compile(
    r"(?:[A-Za-z]:\\[^\s]+|/[^\s]+|\.?\.?/[^\s]+|[\w.-]+\\[\w.-\\]+)"
)
# file.ext
_FILELIKE = re.compile(r"\b[\w.-]+\.\w{1,12}\b")
# pid
_PID = re.compile(r"\b(?:pid|process\s*id)?\s*#?\s*(\d{2,8})\b", re.I)
_PID_SIMPLE = re.compile(r"\b(\d{4,8})\b")


def extract_entities(text: str) -> ExtractedEntities:
    """Pull entities from free text; non-destructive best-effort."""
    t = text.strip()
    out = ExtractedEntities(raw_tokens=t.split())

    # Quoted paths first
    q = _QUOTED.findall(t)
    if q:
        if len(q) >= 2:
            out.source = q[0]
            out.destination = q[1]
        elif not out.path:
            out.path = q[0]

    # copy X to Y / move X to Y (unquoted)
    m = re.search(
        r"\b(?:copy|duplicate|move|rename|mv|cp)\s+([^\s]+)\s+(?:to|into|as)\s+([^\s]+)",
        t,
        re.I,
    )
    if m:
        out.source = out.source or m.group(1).strip("\"'")
        out.destination = out.destination or m.group(2).strip("\"'")

    # cd to path
    m = re.search(r"\b(?:cd|chdir|go to|navigate to)\s+([^\s]+)", t, re.I)
    if m and not out.path:
        out.path = m.group(1).strip("\"'")

    # delete/remove file NAME
    m = re.search(
        r"\b(?:delete|remove|erase|unlink|rm)\s+(?:file\s+)?([^\s]+)", t, re.I
    )
    if m:
        cand = m.group(1).strip("\"'")
        if not cand.startswith("-"):
            out.filename = out.filename or cand

    # cat/read file
    m = re.search(
        r"\b(?:read|cat|show|display|open)\s+(?:file\s+)?([^\s]+)", t, re.I
    )
    if m:
        out.filename = out.filename or m.group(1).strip("\"'")

    # kill process ...
    m = re.search(r"\bkill\s+(?:process\s+)?(?:pid\s*)?#?(\d+)", t, re.I)
    if m:
        out.pid = int(m.group(1))
    m = re.search(r"\bterminate\s+(?:pid\s*)?#?(\d+)", t, re.I)
    if m and out.pid is None:
        out.pid = int(m.group(1))

    m = re.search(r"\b(?:kill|terminate)\s+(?:the\s+)?process\s+([\w.-]+)", t, re.I)
    if m:
        out.process_name = m.group(1)

    # Path-like scan
    for pl in _PATHLIKE.findall(t):
        if not out.path and ("/" in pl or "\\" in pl):
            out.path = pl
            break

    # Filename-like
    for fl in _FILELIKE.findall(t):
        if not out.filename:
            out.filename = fl
            break

    if out.pid is None:
        pm = _PID.search(t)
        if pm:
            out.pid = int(pm.group(1))
        else:
            for sm in _PID_SIMPLE.finditer(t):
                n = int(sm.group(1))
                if 1000 <= n <= 99999999:
                    out.pid = n
                    break

    # ping <host>
    m = re.search(
        r"\bping\s+([a-zA-Z0-9][a-zA-Z0-9.-]*|[0-9]{1,3}(?:\.[0-9]{1,3}){3})\b",
        t,
        re.I,
    )
    if m:
        out.host = m.group(1)

    # mkdir / make directory / md <path>
    m = re.search(
        r"\b(?:mkdir|md|make\s+directory|create\s+(?:a\s+)?folder)\s+([^\s]+)",
        t,
        re.I,
    )
    if m and not out.path:
        out.path = m.group(1).strip("\"'")

    # grep <pattern> [file]
    m = re.search(
        r"\b(?:grep|rg|ripgrep)\s+(?:-[^\s]+\s+)*['\"]?([^'\"\s]+)['\"]?(?:\s+([^\s]+))?",
        t,
        re.I,
    )
    if m:
        out.pattern = out.pattern or m.group(1)
        if m.lastindex and m.lastindex >= 2 and m.group(2):
            fn = m.group(2)
            if not fn.startswith("-"):
                out.filename = out.filename or fn

    # find *.<ext> or name <x>
    m = re.search(r"\*\.(\w{1,8})\b", t)
    if m:
        out.pattern = out.pattern or f"*.{m.group(1)}"
    m = re.search(r"\b(?:named?|called)\s+['\"]?([\w.*-]+)['\"]?", t, re.I)
    if m and not out.pattern:
        out.pattern = m.group(1)

    return out


def entities_to_dict(e: ExtractedEntities) -> Dict[str, object]:
    """JSON-serializable entity dict (omit Nones)."""
    d: Dict[str, object] = {}
    if e.path is not None:
        d["path"] = e.path
    if e.filename is not None:
        d["filename"] = e.filename
    if e.source is not None:
        d["source"] = e.source
    if e.destination is not None:
        d["destination"] = e.destination
    if e.pid is not None:
        d["pid"] = e.pid
    if e.process_name is not None:
        d["process_name"] = e.process_name
    if e.host is not None:
        d["host"] = e.host
    if e.pattern is not None:
        d["pattern"] = e.pattern
    return d
