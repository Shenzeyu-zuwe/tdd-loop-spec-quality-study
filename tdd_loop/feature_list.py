# -*- coding: utf-8 -*-
"""
Feature list — the spec artifact consumed by the TDD loop.

Design: *intent-only*. Each feature and each test carries a natural-language
intent string but NO test code. The Tester agent reads the code base at
runtime, decides how to verify, and executes. This avoids the failure mode
where pre-written test code is authored blind by an AI and encodes the wrong
attribute names, import paths, or call conventions.

JSON schema:
    {
      "change_name": "...",
      "spec_dir":    "optional path to human-readable spec",
      "features": [
        {
          "id": "F-001",
          "intent": "Natural-language description of the capability",
          "status": "pending|in_progress|passed|failed|skipped",
          "dependencies": ["F-000", ...],
          "test_cases": [
            {
              "id": "T-001-01",
              "intent": "Natural-language description of one observable check",
              "status": "pending|passed|failed|skipped",
              "reason": "last Tester explanation (set by loop)"
            }
          ]
        }
      ],
      "summary": {...}  # rewritten on every save
    }
"""

import hashlib
import json
import re
from datetime import datetime


class FeatureList:
    """Read/write wrapper over a feature_list.json file with state-transition helpers."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: dict = {}

    def load(self) -> "FeatureList":
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        return self

    def save(self) -> "FeatureList":
        self._update_summary()
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        return self

    # ── Queries ──────────────────────────────────────────────────

    def all_passed(self) -> bool:
        features = self.data.get("features", [])
        return bool(features) and all(f["status"] in ("passed", "skipped") for f in features)

    def get_next_feature(self) -> dict | None:
        """Return the next actionable feature honouring dependencies. Failed > pending."""
        features = self.data.get("features", [])
        done_ids = {f["id"] for f in features if f["status"] in ("passed", "skipped")}
        ready = []
        for f in features:
            if f["status"] in ("passed", "skipped"):
                continue
            deps = f.get("dependencies", [])
            if all(d in done_ids for d in deps):
                ready.append(f)
        ready.sort(key=lambda f: 0 if f["status"] == "failed" else 1)
        return ready[0] if ready else None

    def get_failed_tests(self, feature_id: str) -> list[dict]:
        for f in self.data.get("features", []):
            if f["id"] == feature_id:
                return [t for t in f.get("test_cases", []) if t["status"] == "failed"]
        return []

    def get_feature(self, feature_id: str) -> dict | None:
        for f in self.data.get("features", []):
            if f["id"] == feature_id:
                return f
        return None

    # ── Mutators ─────────────────────────────────────────────────

    def update_test(self, test_id: str, status: str, reason: str = "") -> bool:
        for f in self.data.get("features", []):
            for t in f.get("test_cases", []):
                if t["id"] == test_id:
                    t["status"] = status
                    t["reason"] = reason
                    t["last_run"] = datetime.now().isoformat()
                    self._sync_feature_status(f)
                    return True
        return False

    def update_feature_status(self, feature_id: str, status: str):
        for f in self.data.get("features", []):
            if f["id"] == feature_id:
                f["status"] = status
                return

    # ── Internals ────────────────────────────────────────────────

    def _sync_feature_status(self, feature: dict):
        tests = feature.get("test_cases", [])
        if not tests:
            return
        statuses = [t["status"] for t in tests]
        if all(s == "passed" for s in statuses):
            feature["status"] = "passed"
        elif any(s == "failed" for s in statuses):
            feature["status"] = "failed"
        elif any(s == "pending" for s in statuses):
            feature["status"] = "in_progress"
        elif all(s == "skipped" for s in statuses):
            feature["status"] = "skipped"
        elif any(s == "skipped" for s in statuses):
            feature["status"] = "skipped"

    def _update_summary(self):
        features = self.data.get("features", [])
        all_tests = [t for f in features for t in f.get("test_cases", [])]
        self.data["summary"] = {
            "total_features": len(features),
            "passed": sum(1 for f in features if f["status"] == "passed"),
            "failed": sum(1 for f in features if f["status"] == "failed"),
            "pending": sum(1 for f in features if f["status"] in ("pending", "in_progress")),
            "total_tests": len(all_tests),
            "tests_passed": sum(1 for t in all_tests if t["status"] == "passed"),
            "tests_failed": sum(1 for t in all_tests if t["status"] == "failed"),
            "tests_pending": sum(1 for t in all_tests if t["status"] == "pending"),
            "tests_skipped": sum(1 for t in all_tests if t["status"] == "skipped"),
        }

    def get_progress_report(self) -> str:
        self._update_summary()
        s = self.data.get("summary", {})
        icon = {
            "passed": "[PASS]", "failed": "[FAIL]", "pending": "[....]",
            "in_progress": "[>>  ]", "skipped": "[SKIP]",
        }
        lines = [
            "=== TDD Loop Progress ===",
            f"Features: {s.get('passed', 0)}/{s.get('total_features', 0)} passed"
            f"  ({s.get('failed', 0)} failed, {s.get('pending', 0)} pending)",
            f"Tests:    {s.get('tests_passed', 0)}/{s.get('total_tests', 0)} passed"
            f"  ({s.get('tests_failed', 0)} failed, {s.get('tests_pending', 0)} pending)",
            "",
        ]
        for f in self.data.get("features", []):
            lines.append(f"  {icon.get(f['status'], '[????]')} {f['id']} {f['intent'][:60]}")
            for t in f.get("test_cases", []):
                lines.append(f"    {icon.get(t['status'], '[????]')} {t['id']} {t['intent'][:60]}")
        return "\n".join(lines)

    def signature(self) -> str:
        """Stable hash over (feature_id, test_id, intent) triples. Ignores runtime
        fields so edits to status/reason/last_run don't invalidate caches."""
        triples = []
        for f in self.data.get("features", []):
            fid = f.get("id", "")
            triples.append((fid, "", f.get("intent", ""), tuple(f.get("dependencies", []) or [])))
            for t in f.get("test_cases", []) or []:
                triples.append((fid, t.get("id", ""), t.get("intent", ""), ()))
        payload = json.dumps(triples, ensure_ascii=False, sort_keys=False)
        return hashlib.md5(payload.encode("utf-8")).hexdigest()


def create_empty_feature_list(change_name: str, spec_dir: str = "") -> dict:
    return {
        "change_name": change_name,
        "created_at": datetime.now().isoformat(),
        "spec_dir": spec_dir,
        "features": [],
        "summary": {},
    }


# ── Intent anchor linter ────────────────────────────────────────
#
# An "anchor" is a concrete, programmatically checkable token — identifier,
# operator, API call, file extension, etc. — that pins an intent to a specific
# code-level artifact. Anchorless intents ("UI looks right") let the Tester
# confabulate passes based on visual similarity. Anchored intents ("expect
# response.status_code == 200") force the Tester to probe a specific surface.
#
# The default pattern set targets generic software cues. Projects can extend
# it with domain-specific anchors via the `extra_anchors` argument.

_DEFAULT_ANCHOR_PATTERNS = [
    r"==", r"!=", r">=", r"<=",
    r"\bassert\b", r"\braise\b",
    r"\bclass\s+\w+", r"\bdef\s+\w+", r"\bimport\s+\w+", r"\bfrom\s+\w+\s+import",
    r"\breturn\b",
    r"\bHTTP\s*\d{3}\b", r"\bstatus_code\b",
    r"\.[a-zA-Z_]\w*\(",          # method call
    r"[A-Z_]{2,}\b",              # CONSTANT
    r"\.\w+\s*=\s*",              # attribute assignment
    r"`[^`]+`",                   # any backticked symbol
    r"#\d+",                      # ticket ref
    r"\bfile\s+\w+\.\w+",         # "file foo.py"
    r"\b[a-z_]\w+\.py\b",         # Python filename
]


def lint_intents(data: dict, extra_anchors: list[str] | None = None) -> list[dict]:
    """Flag test intents lacking any programmatic verification anchor.

    Returns a list of {level, id, intent, hint} warnings. Warnings are
    advisory; the loop runs regardless. The point is to surface anchorless
    intents at startup so the author knows they risk false passes.
    """
    patterns = list(_DEFAULT_ANCHOR_PATTERNS) + list(extra_anchors or [])
    pattern = re.compile("|".join(patterns), re.IGNORECASE)
    warnings = []
    for f in data.get("features", []):
        for t in f.get("test_cases", []):
            intent = t.get("intent", "")
            if not pattern.search(intent):
                warnings.append({
                    "level": "warn",
                    "id": t["id"],
                    "intent": intent,
                    "hint": ("No programmatic verification anchor found. Tester may "
                             "judge by appearance only, risking false positives. "
                             "Add a concrete token: identifier, operator, API call, "
                             "file name, ticket ref, etc."),
                })
    return warnings
