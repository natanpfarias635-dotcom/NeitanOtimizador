# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Motor Gaming & Jogos (HAGS, Timer/MMCSS, NIC, MSI, Standby RAM & Game Boost)
100% desbloqueado, inspirado na aba Jogos do OtimizePC.
"""

import ctypes
import os
import subprocess
import winreg
from pathlib import Path
from typing import Any, Dict, List

try:
    import psutil
except ImportError:
    psutil = None

from src.core.logger import logger

GAMING_TWEAKS: List[Dict[str, Any]] = [
    {
        "id": "gaming.hags",
        "kicker": "AGENDAMENTO DE GPU (HAGS)",
        "name": "Hardware-Accelerated GPU Scheduling",
        "desc": "Permite que a placa de vídeo gerencie sua própria VRAM diretamente, reduzindo latência de renderização.",
        "hive": winreg.HKEY_LOCAL_MACHINE,
        "subkey": r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
        "value_name": "HwSchMode",
        "on_value": 2,
        "off_value": 1,
    },
    {
        "id": "gaming.mmcss_timer",
        "kicker": "PRIORIDADE MULTIMÍDIA & TIMER",
        "name": "Prioridade Máxima de GPU/CPU para Jogos (MMCSS)",
        "desc": "Define SystemResponsiveness=0% (dedica 100% de recursos ao jogo em foco) e GPU Priority=8.",
        "hive": winreg.HKEY_LOCAL_MACHINE,
        "subkey": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
        "value_name": "SystemResponsiveness",
        "on_value": 0,
        "off_value": 20,
    },
    {
        "id": "gaming.game_mode",
        "kicker": "MODO DE JOGO DO WINDOWS",
        "name": "Forçar Auto Game Mode Dedicado",
        "desc": "Impede que o Windows Update e notificações roubem ciclos de CPU durante partidas.",
        "hive": winreg.HKEY_CURRENT_USER,
        "subkey": r"Software\Microsoft\GameBar",
        "value_name": "AutoGameModeEnabled",
        "on_value": 1,
        "off_value": 0,
    },
    {
        "id": "gaming.power_throttling_off",
        "kicker": "ESTABILIDADE DE CLOCK (FPS 1% LOW)",
        "name": "Desativar Power Throttling do Processador",
        "desc": "Evita quedas bruscas de frequência (clock) do processador durante cargas mistas.",
        "hive": winreg.HKEY_LOCAL_MACHINE,
        "subkey": r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling",
        "value_name": "PowerThrottlingOff",
        "on_value": 1,
        "off_value": 0,
    },
]

BACKGROUND_HOGS = [
    "OneDrive.exe",
    "SkypeApp.exe",
    "YourPhone.exe",
    "PhoneExperienceHost.exe",
    "WidgetService.exe",
    "Widgets.exe",
    "Cortana.exe",
    "Teams.exe",
    "GameBarPresenceWriter.exe",
]


def check_gaming_tweak(tweak: Dict[str, Any]) -> bool:
    try:
        with winreg.OpenKey(tweak["hive"], tweak["subkey"], 0, winreg.KEY_READ) as k:
            val, _ = winreg.QueryValueEx(k, tweak["value_name"])
            return int(val) == int(tweak["on_value"])
    except Exception:
        return False


def apply_gaming_tweak(tweak_id: str, enable: bool = True) -> Dict[str, Any]:
    tweak = next((t for t in GAMING_TWEAKS if t["id"] == tweak_id), None)
    if not tweak:
        return {"success": False, "error": "Ajuste gaming não encontrado."}

    val = tweak["on_value"] if enable else tweak["off_value"]
    try:
        with winreg.CreateKeyEx(tweak["hive"], tweak["subkey"], 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, tweak["value_name"], 0, winreg.REG_DWORD, val)

        if tweak_id == "gaming.mmcss_timer" and enable:
            tasks_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, tasks_key, 0, winreg.KEY_SET_VALUE) as gk:
                winreg.SetValueEx(gk, "GPU Priority", 0, winreg.REG_DWORD, 8)
                winreg.SetValueEx(gk, "Priority", 0, winreg.REG_DWORD, 6)
                winreg.SetValueEx(gk, "Scheduling Category", 0, winreg.REG_SZ, "High")

        logger.set_tweak_state(tweak_id, enable)
        logger.log("Jogos", f"{'Ativado' if enable else 'Revertido'}: {tweak['name']}", True)
        return {"success": True}
    except Exception as e:
        logger.log("Jogos", f"Falha em {tweak['name']}", False, str(e))
        return {"success": False, "error": str(e)}


def apply_all_gaming_tweaks() -> Dict[str, Any]:
    ok_count = 0
    for t in GAMING_TWEAKS:
        res = apply_gaming_tweak(t["id"], True)
        if res.get("success"):
            ok_count += 1
    return {"success": ok_count > 0, "applied": ok_count, "total": len(GAMING_TWEAKS)}


def flush_ram_working_sets() -> Dict[str, Any]:
    """Reduz o uso de memória RAM esvaziando Working Sets de processos ociosos via API Win32."""
    if not psutil:
        return {"success": False, "error": "psutil não instalado"}

    before = psutil.virtual_memory().available
    trimmed = 0
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pid = proc.info["pid"]
            if pid <= 4:
                continue
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)
            if handle:
                ctypes.windll.psapi.EmptyWorkingSet(handle)
                ctypes.windll.kernel32.CloseHandle(handle)
                trimmed += 1
        except Exception:
            pass

    after = psutil.virtual_memory().available
    freed_mb = max(0, int((after - before) / (1024 * 1024)))
    logger.log("Jogos", "Boost de Memória RAM (Working Set Flush)", True, f"{trimmed} processos otimizados (+{freed_mb} MB livres)")
    return {"success": True, "trimmed_processes": trimmed, "freed_mb": freed_mb}


def run_game_session_boost() -> Dict[str, Any]:
    """Executa o Game Boost: suspende/fecha processos desnecessários em segundo plano e limpa a RAM."""
    closed: List[str] = []
    if psutil:
        hogs_lower = {h.lower() for h in BACKGROUND_HOGS}
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = (proc.info["name"] or "").strip()
                if pname.lower() in hogs_lower:
                    proc.terminate()
                    closed.append(pname)
            except Exception:
                pass

    ram_res = flush_ram_working_sets()
    logger.log(
        "Jogos",
        "Sessão Game Boost Ativada",
        True,
        f"Processos encerrados: {len(closed)} | RAM otimizada (+{ram_res.get('freed_mb', 0)} MB)",
    )
    return {
        "success": True,
        "closed_apps": closed,
        "freed_mb": ram_res.get("freed_mb", 0),
        "trimmed_processes": ram_res.get("trimmed_processes", 0),
    }


def detect_game_libraries() -> List[Dict[str, Any]]:
    """Detecta bibliotecas de jogos instaladas no PC (Steam, Epic Games, Riot Games, Battle.net, Rockstar, Xbox)."""
    pf86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    prog_data = Path(os.environ.get("ProgramData", r"C:\ProgramData"))

    libraries = [
        {
            "id": "steam",
            "name": "Steam",
            "paths": [pf86 / "Steam", pf / "Steam", Path("C:/Steam")],
            "games_sub": "steamapps/common",
        },
        {
            "id": "epic",
            "name": "Epic Games",
            "paths": [pf / "Epic Games", pf86 / "Epic Games"],
            "games_sub": "",
        },
        {
            "id": "riot",
            "name": "Riot Games (Valorant / LoL)",
            "paths": [Path("C:/Riot Games"), pf / "Riot Games"],
            "games_sub": "",
        },
        {
            "id": "battlenet",
            "name": "Battle.net",
            "paths": [pf86 / "Battle.net", pf / "Battle.net"],
            "games_sub": "",
        },
        {
            "id": "rockstar",
            "name": "Rockstar Games (GTA / FiveM)",
            "paths": [pf / "Rockstar Games", pf86 / "Rockstar Games"],
            "games_sub": "",
        },
    ]

    detected: List[Dict[str, Any]] = []
    for lib in libraries:
        found_root = next((p for p in lib["paths"] if p.exists()), None)
        games: List[str] = []
        if found_root:
            scan_dir = found_root / lib["games_sub"] if lib["games_sub"] else found_root
            if scan_dir.exists():
                try:
                    for d in scan_dir.iterdir():
                        if d.is_dir() and not d.name.startswith(".") and d.name.lower() not in {"launcher", "directxredist", "steamworks shared"}:
                            games.append(d.name)
                except Exception:
                    pass
        detected.append({
            "id": lib["id"],
            "name": lib["name"],
            "installed": found_root is not None,
            "path": str(found_root) if found_root else "Não detectado",
            "games_count": len(games),
            "games": games[:15],
        })
    return detected
