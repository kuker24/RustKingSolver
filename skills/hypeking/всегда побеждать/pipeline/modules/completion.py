#!/usr/bin/env python3
"""Findings ledger + completion gate — no silent early stops.

A "lead" is anything detected but not finished:
  - a detector finding whose exploit failed or was skipped
  - a router-recommended category that was never executed

Detected-AND-exploited findings never become leads. The gate only opens
when there are no open leads, or the time budget is explicitly exhausted
(pass --force-report to override deliberately).
"""
import json
import os
import time
from typing import List, Tuple, Union

LEAD_FILE = "leads.json"


class CompletionGate:
    """Persistent leads ledger backed by <output_dir>/leads.json."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.path = os.path.join(output_dir, LEAD_FILE)
        self.leads: List[dict] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            self.leads = []
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.leads = data.get("leads", []) if isinstance(data, dict) else []
        except (json.JSONDecodeError, OSError):
            self.leads = []

    def save(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump({"leads": self.leads}, fh, indent=2)

    def add_lead(self, kind: str, detail: str) -> int:
        """Register an open lead; returns its id."""
        lead_id = max((lead["id"] for lead in self.leads), default=0) + 1
        self.leads.append({
            "id": lead_id,
            "kind": kind,
            "detail": detail,
            "status": "open",
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "closed": None,
            "close_reason": None,
        })
        self.save()
        return lead_id

    def close_lead(self, index_or_id: Union[int, dict], reason: str = "closed") -> bool:
        """Close a lead by id, index, or the lead dict itself."""
        if isinstance(index_or_id, dict) and "id" in index_or_id:
            lead = next((l for l in self.leads if l["id"] == index_or_id["id"]), None)
        elif index_or_id in (l["id"] for l in self.leads):
            lead = next(l for l in self.leads if l["id"] == index_or_id)
        else:
            index = int(index_or_id)
            lead = self.leads[index] if 0 <= index < len(self.leads) else None
        if not lead or lead["status"] != "open":
            return False
        lead["status"] = reason
        lead["closed"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        lead["close_reason"] = reason
        self.save()
        return True

    def open_leads(self) -> List[dict]:
        return [lead for lead in self.leads if lead["status"] == "open"]

    def gate(self, budget_exhausted: bool) -> Tuple[bool, str]:
        """Return (may_proceed, message). Blocks while open leads exist and
        the budget is not exhausted."""
        open_leads = self.open_leads()
        if not open_leads:
            return True, "GATE OPEN: no open leads."
        if budget_exhausted:
            return True, (f"GATE OPEN: time budget exhausted with {len(open_leads)} "
                          f"open lead(s) — reporting now, leads preserved.")
        lines = [f"  ├─ [{lead['id']}] {lead['kind']}: {lead['detail']}" for lead in open_leads]
        message = (
            "GATE BLOCKED: open leads remain — finish or close them:\n"
            + "\n".join(lines)
            + "\n  └─ close leads in leads.json, rerun to exhaustion, or pass --force-report."
        )
        return False, message
