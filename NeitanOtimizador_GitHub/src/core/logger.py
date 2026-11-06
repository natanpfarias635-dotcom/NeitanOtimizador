# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Sistema de Logs, Sessões e Estado Persistente
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class AppLogger:
    def __init__(self) -> None:
        import sys
        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).resolve().parent
            self.base_dir = exe_dir / "data"
        else:
            project_root = Path(__file__).resolve().parent.parent.parent
            self.base_dir = project_root / "data"
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            self.base_dir = Path(appdata) / "NeitanOtimizador"
            self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logs_file = self.base_dir / "action_logs.json"
        self.sessions_file = self.base_dir / "sessions.json"
        self.state_file = self.base_dir / "applied_state.json"
        self.schedule_file = self.base_dir / "schedules.json"

    def log(self, module: str, action: str, success: bool, details: str = "") -> Dict[str, Any]:
        entry = {
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "module": module,
            "action": action,
            "success": success,
            "details": details,
        }
        logs = self.get_logs()
        logs.insert(0, entry)
        logs = logs[:500]  # Mantém os últimos 500 registros
        self._write_json(self.logs_file, logs)
        return entry

    def get_logs(self) -> List[Dict[str, Any]]:
        return self._read_json(self.logs_file, [])

    def clear_logs(self) -> None:
        self._write_json(self.logs_file, [])

    def record_session(self, profile_id: str, profile_name: str, items_applied: List[str], failed_count: int = 0) -> Dict[str, Any]:
        session = {
            "sessionId": f"sess_{int(time.time())}",
            "profile": profile_id,
            "profileName": profile_name,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "itemCount": len(items_applied),
            "failedCount": failed_count,
            "items": items_applied,
        }
        sessions = self.get_sessions()
        sessions.insert(0, session)
        sessions = sessions[:50]
        self._write_json(self.sessions_file, sessions)
        return session

    def get_sessions(self) -> List[Dict[str, Any]]:
        return self._read_json(self.sessions_file, [])

    def get_applied_state(self) -> Dict[str, Any]:
        return self._read_json(self.state_file, {"tweaks": {}, "active_profile": None, "last_opt": None})

    def set_tweak_state(self, key: str, applied: bool, active_profile: Optional[str] = None) -> None:
        state = self.get_applied_state()
        if "tweaks" not in state:
            state["tweaks"] = {}
        state["tweaks"][key] = applied
        state["last_opt"] = datetime.now().strftime("%d/%m/%Y às %H:%M")
        if active_profile is not None:
            state["active_profile"] = active_profile
        self._write_json(self.state_file, state)

    def _read_json(self, path: Path, default: Any) -> Any:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return default

    def _write_json(self, path: Path, data: Any) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


logger = AppLogger()
