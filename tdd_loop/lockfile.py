# -*- coding: utf-8 -*-
"""
Per-change orchestrator singleton lock.

Ensures at most one orchestrator runs against a given feature_list.json at a
time. Different feature lists can run concurrently — each gets its own lock
file next to its feature_list.json.
"""

import json
import os
import sys
import time
from pathlib import Path


def _is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    except OSError:
        return False
    return True


class AutoLoopLock:
    def __init__(self, lock_path: Path):
        self.lock_path = Path(lock_path)
        self._acquired = False

    def acquire(self) -> tuple[bool, str]:
        if self.lock_path.exists():
            existing = self._read_lock()
            if existing is not None:
                existing_pid = existing.get("pid", 0)
                if _is_pid_alive(existing_pid):
                    return False, (
                        f"Another orchestrator is already running:\n"
                        f"  Change:   {existing.get('change_name', '?')}\n"
                        f"  PID:      {existing_pid}\n"
                        f"  Started:  {existing.get('started_at', '?')}\n"
                        f"  Lock:     {self.lock_path}\n"
                    )
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "pid": os.getpid(),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "cwd": os.getcwd(),
            "change_name": self.lock_path.parent.name,
        }
        self.lock_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        self._acquired = True
        return True, f"Lock acquired: {self.lock_path}"

    def release(self) -> None:
        if not self._acquired:
            return
        try:
            if self.lock_path.exists():
                existing = self._read_lock()
                if existing and existing.get("pid") == os.getpid():
                    self.lock_path.unlink()
        except OSError:
            pass
        self._acquired = False

    def read_lock_data(self) -> dict | None:
        if not self.lock_path.exists():
            return None
        return self._read_lock()

    def force_remove(self) -> None:
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except OSError:
            pass
        self._acquired = False

    def _read_lock(self) -> dict | None:
        try:
            return json.loads(self.lock_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, ValueError):
            return None

    def __enter__(self):
        ok, msg = self.acquire()
        if not ok:
            raise RuntimeError(msg)
        return self

    def __exit__(self, *exc):
        self.release()
