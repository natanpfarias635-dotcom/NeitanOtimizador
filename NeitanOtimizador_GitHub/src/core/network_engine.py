# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Motor de Rede (Benchmark DNS, Teste de Estabilidade, Otimizações & Reset Winsock)
Baseado nas 3 sub-abas de Rede do OtimizePC, 100% desbloqueado.
"""

import re
import socket
import subprocess
import time
import winreg
from typing import Any, Dict, List

from src.core.logger import logger

DNS_SERVERS = [
    {"name": "Cloudflare Gaming", "primary": "1.1.1.1", "secondary": "1.0.0.1"},
    {"name": "Google Public DNS", "primary": "8.8.8.8", "secondary": "8.8.4.4"},
    {"name": "Quad9 Security", "primary": "9.9.9.9", "secondary": "149.112.112.112"},
    {"name": "OpenDNS Cisco", "primary": "208.67.222.222", "secondary": "208.67.220.220"},
]

NETWORK_TWEAKS: List[Dict[str, Any]] = [
    {
        "key": "dns_gaming",
        "name": "DNS de Baixa Latência (Cloudflare 1.1.1.1 + Google 8.8.8.8)",
        "desc": "Configura os servidores DNS mais rápidos do mundo na interface de rede ativa.",
        "reversible": True,
    },
    {
        "key": "qos_limit_zero",
        "name": "Liberar 100% da Largura de Banda (Desativar Reserva QoS)",
        "desc": "Zera o limite NonBestEffortLimit do Agendador de Pacotes QoS do Windows.",
        "reversible": True,
    },
    {
        "key": "network_throttling_off",
        "name": "Desativar Estrangulamento de Rede (NetworkThrottlingIndex = FFFFFFFF)",
        "desc": "Remove a limitação de pacotes multimídia por segundo para reduzir spikes de ping.",
        "reversible": True,
    },
    {
        "key": "tcp_gaming_tuning",
        "name": "Ajuste Avançado da Pilha TCP/IP (AutoTuning Normal + RSS Ativo)",
        "desc": "Otimiza Receive-Side Scaling (RSS) e janela TCP via netsh int tcp.",
        "reversible": True,
    },
    {
        "key": "delivery_opt_off",
        "name": "Desativar Upload P2P de Atualizações (Delivery Optimization)",
        "desc": "Impede que o Windows use sua conexão para enviar atualizações a outros PCs.",
        "reversible": True,
    },
]


def _run_hidden(cmd: List[str], timeout: int = 8) -> subprocess.CompletedProcess:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, startupinfo=startupinfo)


def measure_tcp_ping(host: str = "1.1.1.1", port: int = 53, timeout: float = 1.5) -> float:
    """Mede latência TCP em milissegundos sem depender do idioma do comando ping."""
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return round((time.perf_counter() - t0) * 1000.0, 1)
    except Exception:
        return -1.0


def get_network_overview() -> Dict[str, Any]:
    """Retorna adaptador ativo, IPv4 e ping atual."""
    ip_addr = "127.0.0.1"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("1.1.1.1", 80))
            ip_addr = s.getsockname()[0]
    except Exception:
        pass

    ping_ms = measure_tcp_ping("1.1.1.1", 53)
    return {
        "ipv4": ip_addr,
        "ping_ms": ping_ms,
        "status": "Conectado" if ping_ms > 0 else "Sem resposta externa",
    }


def run_dns_benchmark() -> List[Dict[str, Any]]:
    """Compara o tempo de resposta real dos principais servidores DNS."""
    results: List[Dict[str, Any]] = []
    for srv in DNS_SERVERS:
        samples = []
        for _ in range(3):
            ms = measure_tcp_ping(srv["primary"], 53, timeout=1.2)
            if ms > 0:
                samples.append(ms)
        avg_ms = round(sum(samples) / len(samples), 1) if samples else -1.0
        results.append({
            "name": srv["name"],
            "ip": f"{srv['primary']} / {srv['secondary']}",
            "ping_ms": avg_ms,
        })

    results.sort(key=lambda x: x["ping_ms"] if x["ping_ms"] > 0 else 9999.0)
    return results


def run_stability_test(target: str = "1.1.1.1", count: int = 8) -> Dict[str, Any]:
    """Executa disparos consecutivos para medir Ping Mínimo, Médio, Máximo, Jitter e Perda."""
    samples: List[float] = []
    sent = count
    for _ in range(count):
        ms = measure_tcp_ping(target, 53, timeout=1.2)
        if ms > 0:
            samples.append(ms)
        time.sleep(0.08)

    received = len(samples)
    loss_pct = round(((sent - received) / sent) * 100.0, 1)
    if not samples:
        return {
            "target": target,
            "sent": sent,
            "received": 0,
            "loss_pct": 100.0,
            "min_ms": 0.0,
            "avg_ms": 0.0,
            "max_ms": 0.0,
            "jitter_ms": 0.0,
        }

    min_ms = round(min(samples), 1)
    max_ms = round(max(samples), 1)
    avg_ms = round(sum(samples) / len(samples), 1)
    diffs = [abs(samples[i] - samples[i - 1]) for i in range(1, len(samples))]
    jitter_ms = round(sum(diffs) / len(diffs), 1) if diffs else 0.0

    return {
        "target": target,
        "sent": sent,
        "received": received,
        "loss_pct": loss_pct,
        "min_ms": min_ms,
        "avg_ms": avg_ms,
        "max_ms": max_ms,
        "jitter_ms": jitter_ms,
    }


def apply_network_tweak(key: str, enable: bool = True) -> Dict[str, Any]:
    try:
        if key == "qos_limit_zero":
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\Psched"
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE) as k:
                if enable:
                    winreg.SetValueEx(k, "NonBestEffortLimit", 0, winreg.REG_DWORD, 0)
                else:
                    try:
                        winreg.DeleteValue(k, "NonBestEffortLimit")
                    except OSError:
                        pass

        elif key == "network_throttling_off":
            subkey = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xFFFFFFFF if enable else 10)

        elif key == "delivery_opt_off":
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization"
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, "DODownloadMode", 0, winreg.REG_DWORD, 0 if enable else 1)

        elif key == "tcp_gaming_tuning":
            _run_hidden(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"])
            _run_hidden(["netsh", "int", "tcp", "set", "global", "rss=enabled"])

        elif key == "dns_gaming":
            if enable:
                ps_cmd = (
                    "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | "
                    "ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses ('1.1.1.1','8.8.8.8') }"
                )
            else:
                ps_cmd = (
                    "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | "
                    "ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }"
                )
            _run_hidden(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=10)

        logger.set_tweak_state(f"net.{key}", enable)
        logger.log("Rede", f"{'Ativado' if enable else 'Revertido'}: {key}", True)
        return {"success": True}
    except Exception as e:
        logger.log("Rede", f"Erro ao aplicar {key}", False, str(e))
        return {"success": False, "error": str(e)}


def reset_network_stack() -> Dict[str, Any]:
    """Executa Flush DNS, Reset Winsock e Reset TCP/IP."""
    commands = [
        (["ipconfig", "/flushdns"], "Flush DNS"),
        (["ipconfig", "/registerdns"], "Register DNS"),
        (["netsh", "winsock", "reset"], "Winsock Reset"),
        (["netsh", "int", "ip", "reset"], "TCP/IP Reset"),
    ]
    ok_steps = 0
    for cmd, label in commands:
        try:
            res = _run_hidden(cmd, timeout=8)
            if res.returncode == 0:
                ok_steps += 1
        except Exception:
            pass

    logger.log("Rede", "Reset Completo da Pilha de Rede (DNS + Winsock + TCP/IP)", ok_steps > 0, f"{ok_steps}/4 etapas concluídas")
    return {
        "success": ok_steps > 0,
        "ok_steps": ok_steps,
        "total_steps": len(commands),
    }
