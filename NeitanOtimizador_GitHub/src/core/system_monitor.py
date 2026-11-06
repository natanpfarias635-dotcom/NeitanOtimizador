# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Monitoramento em Tempo Real do Sistema (CPU, RAM, Disco, Rede, Hardware, WinSAT)
"""

import ctypes
import os
import platform
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict

try:
    import psutil
except ImportError:
    psutil = None


def is_user_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def get_live_metrics() -> Dict[str, Any]:
    """Coleta métricas em tempo real de CPU, RAM, Disco e Uptime."""
    if not psutil:
        return {
            "cpu_percent": 0.0,
            "ram_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "disk_percent": 0.0,
            "disk_free_gb": 0.0,
            "disk_total_gb": 0.0,
            "uptime_str": "--",
            "process_count": 0,
            "health_score": 100,
            "health_label": "RECURSOS OK",
        }

    try:
        cpu = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        sys_drive = os.environ.get("SystemDrive", "C:") + "\\"
        disk = psutil.disk_usage(sys_drive)

        boot_time = psutil.boot_time()
        uptime_sec = max(0, int(time.time() - boot_time))
        hours = uptime_sec // 3600
        mins = (uptime_sec % 3600) // 60
        uptime_str = f"{hours}h {mins}min" if hours > 0 else f"{mins} min"

        proc_count = len(psutil.pids())

        # Cálculo de Saúde de Recursos (0 a 100, igual à referência do Painel)
        penalty = (cpu * 0.35) + (vm.percent * 0.40) + (max(0, disk.percent - 70) * 0.5)
        health_score = max(15, min(100, int(100 - penalty * 0.6)))
        if health_score >= 75:
            health_label = "RECURSOS OK"
        elif health_score >= 50:
            health_label = "ATENÇÃO"
        else:
            health_label = "CRÍTICO"

        return {
            "cpu_percent": round(cpu, 1),
            "ram_percent": round(vm.percent, 1),
            "ram_used_gb": round(vm.used / (1024**3), 1),
            "ram_total_gb": round(vm.total / (1024**3), 1),
            "disk_percent": round(disk.percent, 1),
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "uptime_str": uptime_str,
            "process_count": proc_count,
            "health_score": health_score,
            "health_label": health_label,
        }
    except Exception:
        return {
            "cpu_percent": 0.0,
            "ram_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "disk_percent": 0.0,
            "disk_free_gb": 0.0,
            "disk_total_gb": 0.0,
            "uptime_str": "--",
            "process_count": 0,
            "health_score": 85,
            "health_label": "RECURSOS OK",
        }


def get_hardware_summary() -> Dict[str, str]:
    """Obtém informações do Processador, GPU, RAM e Windows."""
    cpu_name = platform.processor() or "Processador x64"
    gpu_name = "GPU Padrão do Sistema"
    os_name = f"Windows {platform.release()} ({platform.version()})"

    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            "$cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1).Name; "
            "$gpu = (Get-CimInstance Win32_VideoController | Select-Object -First 1).Name; "
            "$os = (Get-CimInstance Win32_OperatingSystem).Caption; "
            "Write-Output \"$cpu|$gpu|$os\"",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=6, startupinfo=startupinfo)
        if res.returncode == 0 and "|" in res.stdout:
            parts = res.stdout.strip().split("|")
            if len(parts) >= 3:
                cpu_name = parts[0].strip() or cpu_name
                gpu_name = parts[1].strip() or gpu_name
                os_name = parts[2].strip() or os_name
    except Exception:
        pass

    ram_gb = "8 GB"
    if psutil:
        try:
            ram_gb = f"{round(psutil.virtual_memory().total / (1024**3))} GB RAM"
        except Exception:
            pass

    return {
        "cpu": cpu_name,
        "gpu": gpu_name,
        "ram": ram_gb,
        "os": os_name,
    }


def get_winsat_scores() -> Dict[str, Any]:
    """Lê a nota oficial de hardware do Windows (WinSAT DataStore) como no OtimizePC."""
    datastore = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Performance" / "WinSAT" / "DataStore"
    result = {
        "evaluated": False,
        "base": 0.0,
        "cpu": 0.0,
        "memory": 0.0,
        "graphics": 0.0,
        "gaming": 0.0,
        "disk": 0.0,
    }
    try:
        if not datastore.exists():
            return result
        xml_files = sorted(datastore.glob("*Formal.Assessment*.WinSAT.xml"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not xml_files:
            return result
        tree = ET.parse(xml_files[0])
        root = tree.getroot()
        win_spr = root.find("WinSPR")
        if win_spr is None:
            return result

        def _val(tag: str) -> float:
            el = win_spr.find(tag)
            if el is not None and el.text:
                return float(el.text.replace(",", "."))
            return 0.0

        result["base"] = _val("SystemScore")
        result["cpu"] = _val("CpuScore")
        result["memory"] = _val("MemoryScore")
        result["graphics"] = _val("GraphicsScore")
        result["gaming"] = _val("GamingScore")
        result["disk"] = _val("DiskScore")
        result["evaluated"] = result["base"] > 0
    except Exception:
        pass
    return result
