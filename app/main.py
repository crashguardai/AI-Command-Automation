"""
FastAPI application: REST API + simple dashboard for NLP command automation.

Endpoints:
- ``GET /`` — web UI to try utterances and inspect mapped commands.
- ``POST /api/interpret`` — NLU only (intent + entities + probabilities).
- ``POST /api/command`` — full pipeline including mapping and safety evaluation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

from app.command_mapping.mapper import map_command
from app.logging_config import log_interaction
from app.nlu.pipeline import interpret, nlu_result_to_dict
from app.safety.layer import SafetyResult, evaluate_safety

# Project root: .../app/main.py -> parent.parent
BASE_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_HTML = BASE_DIR / "templates" / "dashboard.html"

app = FastAPI(
    title="NLP Command Automation",
    description="Natural language to shell commands with safety checks",
    version="1.0.0",
)


class InterpretRequest(BaseModel):
    text: str = Field(..., min_length=1, description="User natural language instruction")


class CommandRequest(BaseModel):
    text: str = Field(..., min_length=1)
    # Optional override for command generation (nt = Windows, posix = Unix-like).
    target_os: Optional[str] = Field(
        default=None,
        description="Force 'nt' or 'posix'; default is runtime OS.",
    )
    user_confirmed: bool = Field(
        default=False,
        description="Set true if the user already acknowledged high-risk actions.",
    )


def _target_os_name(req_os: Optional[str]) -> str:
    if req_os == "posix":
        return "posix"
    if req_os == "nt":
        return "nt"
    return os.name


def _load_dashboard_html() -> str:
    if not DASHBOARD_HTML.is_file():
        raise FileNotFoundError(str(DASHBOARD_HTML))
    return DASHBOARD_HTML.read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    """
    Single self-contained HTML page (CSS inlined in template) so the browser
    does not need a separate /static request — avoids 404s from StaticFiles mounts.
    """
    try:
        return HTMLResponse(content=_load_dashboard_html())
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Missing dashboard template: {e}") from e
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Cannot read dashboard: {e}") from e


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> PlainTextResponse:
    """Avoid noisy 404s in browser devtools."""
    return PlainTextResponse("", status_code=204)


@app.get("/api/debug-paths")
async def debug_paths() -> Dict[str, Any]:
    """Use this if the UI fails: confirms which files the running server resolves."""
    return {
        "base_dir": str(BASE_DIR),
        "dashboard_exists": DASHBOARD_HTML.is_file(),
        "dashboard_path": str(DASHBOARD_HTML),
    }


@app.post("/api/interpret")
async def api_interpret(body: InterpretRequest) -> Dict[str, Any]:
    """Return intent classification and extracted entities only."""
    nlu = interpret(body.text)
    return nlu_result_to_dict(nlu)


@app.post("/api/command")
async def api_command(body: CommandRequest) -> Dict[str, Any]:
    """
    Full pipeline: NLU → command mapping → safety.

    This API does **not** execute shell commands; it returns the proposed
    command string. Set ``user_confirmed`` only after your UI collects an
    explicit confirmation for high-risk operations.
    """
    nlu = interpret(body.text)
    tgt = _target_os_name(body.target_os)
    mapped = map_command(nlu, target_os=tgt)
    safety: SafetyResult = evaluate_safety(nlu.intent, mapped)

    blocked_by_safety = safety.requires_confirmation and not body.user_confirmed
    # User must confirm before treating the command as "approved" in a client.
    approved = not blocked_by_safety and not mapped.ambiguous and mapped.command

    out: Dict[str, Any] = {
        "intent": nlu.intent,
        "confidence": nlu.confidence,
        "entities": nlu_result_to_dict(nlu)["entities"],
        "probabilities": nlu.probabilities,
        "fallback_reason": nlu.fallback_reason,
        "command": mapped.command,
        "commands": mapped.commands,
        "explanation": mapped.explanation,
        "ambiguous": mapped.ambiguous,
        "risk_level": safety.risk_level.value,
        "requires_confirmation": safety.requires_confirmation,
        "safety_reason": safety.reason,
        "user_confirmed": body.user_confirmed,
        "blocked_until_confirmation": blocked_by_safety,
        "approved_for_display": bool(approved),
        "target_os": tgt,
    }

    log_interaction(
        {
            "endpoint": "/api/command",
            "input": body.text,
            "intent": nlu.intent,
            "confidence": nlu.confidence,
            "command": mapped.command,
            "risk": safety.risk_level.value,
            "requires_confirmation": safety.requires_confirmation,
        }
    )
    return out


@app.get("/api/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
