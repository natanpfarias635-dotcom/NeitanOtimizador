# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Atualizações (Winget), Pontos de Restauração e Agendador de Tarefas
"""

import subprocess
from datetime import datetime
from typing import Any, Dict, List

from src.core.logger import logger


def _run_hidden(cmd: List[str], timeout: int = 25) -> subprocess.CompletedProcess:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, startupinfo=startupinfo, encoding="utf-8", errors="ignore")


def create_restore_point(description: str = "NeitanOtimizador - Backup Automático") -> Dict[str, Any]:
    """
    Ativa a Proteção do Sistema no disco principal (caso desligada),
    remove o limite de 1 ponto a cada 24h do Windows (SystemRestorePointCreationFrequency = 0)
    e cria um Ponto de Restauração oficial via Checkpoint-Computer.
    """
    try:
        ps_cmd = (
            "$ErrorActionPreference = 'Stop'; "
            "New-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore' "
            "-Name 'SystemRestorePointCreationFrequency' -Value 0 -PropertyType DWord -Force | Out-Null; "
            "Enable-ComputerRestore -Drive \"$env:SystemDrive\\\" -ErrorAction SilentlyContinue; "
            f"Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS'"
        )
        res = _run_hidden(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=60)
        ok = res.returncode == 0
        logger.log(
            "Segurança",
            f"Ponto de Restauração: {description}",
            ok,
            "Criado com sucesso no Windows (System Volume Information)" if ok else (res.stderr.strip() or "Execute como Administrador"),
        )
        return {
            "success": ok,
            "error": res.stderr.strip() if not ok else "",
        }
    except Exception as e:
        logger.log("Segurança", "Falha ao criar Ponto de Restauração", False, str(e))
        return {"success": False, "error": str(e)}


def open_windows_restore_ui() -> None:
    """Abre a interface oficial de Restauração do Sistema do Windows (rstrui.exe)."""
    try:
        subprocess.Popen(["rstrui.exe"])
    except Exception:
        try:
            subprocess.Popen(["SystemPropertiesProtection.exe"])
        except Exception:
            pass


def list_restore_points() -> List[Dict[str, str]]:
    """Lista os Pontos de Restauração existentes no Windows."""
    points: List[Dict[str, str]] = []
    try:
        ps_cmd = (
            "Get-ComputerRestorePoint | Select-Object SequenceNumber, Description, CreationTime | "
            "ForEach-Object { Write-Output \"$($_.SequenceNumber)|$($_.Description)|$($_.CreationTime)\" }"
        )
        res = _run_hidden(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=12)
        if res.returncode == 0 and res.stdout:
            for line in res.stdout.strip().splitlines():
                if "|" in line:
                    parts = line.split("|")
                    points.append({
                        "id": parts[0].strip(),
                        "description": parts[1].strip(),
                        "created_at": parts[2].strip(),
                    })
    except Exception:
        pass
    return points


def check_winget_updates() -> List[Dict[str, str]]:
    """Lista programas que possuem atualização disponível via Winget."""
    updates: List[Dict[str, str]] = []
    try:
        res = _run_hidden(["winget", "upgrade", "--accept-source-agreements"], timeout=30)
        lines = res.stdout.splitlines()
        header_passed = False
        for line in lines:
            if line.strip().startswith("---"):
                header_passed = True
                continue
            if not header_passed or not line.strip():
                continue
            if "atualizações disponíveis" in line.lower() or "upgrades available" in line.lower():
                continue
            parts = line.split()
            if len(parts) >= 4:
                avail_ver = parts[-2] if parts[-1].lower() in ("winget", "msstore") else parts[-1]
                curr_ver = parts[-3] if parts[-1].lower() in ("winget", "msstore") else parts[-2]
                pkg_id = parts[-4] if parts[-1].lower() in ("winget", "msstore") else parts[-3]
                name = " ".join(parts[:-4]) if parts[-1].lower() in ("winget", "msstore") else " ".join(parts[:-3])
                if name and pkg_id and "." in pkg_id:
                    updates.append({
                        "name": name[:45],
                        "id": pkg_id,
                        "current": curr_ver,
                        "available": avail_ver,
                    })
    except Exception:
        pass
    return updates[:40]


def upgrade_all_winget() -> Dict[str, Any]:
    """Dispara a atualização silenciosa de pacotes via winget."""
    try:
        res = _run_hidden(
            ["winget", "upgrade", "--all", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
            timeout=120,
        )
        ok = res.returncode == 0
        logger.log("Atualizações", "Winget Upgrade All executado", ok)
        return {"success": ok, "output": res.stdout[-400:] if res.stdout else ""}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_schedules() -> List[Dict[str, Any]]:
    return logger._read_json(logger.schedule_file, [])


def save_schedule(job_type: str, recurrence: str, time_str: str, only_idle: bool = True) -> Dict[str, Any]:
    schedules = get_schedules()
    entry = {
        "id": f"sched_{int(datetime.now().timestamp())}",
        "job_type": job_type,
        "recurrence": recurrence,
        "time": time_str,
        "only_idle": only_idle,
        "enabled": True,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    schedules.insert(0, entry)
    logger._write_json(logger.schedule_file, schedules)
    logger.log("Agendador", f"Tarefa agendada criada: {job_type} ({recurrence} às {time_str})", True)
    return entry


def delete_schedule(sched_id: str) -> None:
    schedules = [s for s in get_schedules() if s.get("id") != sched_id]
    logger._write_json(logger.schedule_file, schedules)
    logger.log("Agendador", f"Tarefa removida: {sched_id}", True)
