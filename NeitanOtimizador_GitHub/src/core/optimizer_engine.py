# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Motor de Otimizações (Visual, Serviços, Energia, Inicialização, Apps)
Baseado nas 5 sub-abas de Otimizações do OtimizePC, 100% desbloqueado.
"""

import subprocess
import winreg
from typing import Any, Dict, List

from src.core.logger import logger

VISUAL_TWEAKS: List[Dict[str, Any]] = [
    {
        "id": "visual.disable_animations",
        "name": "Desativar Animações Visuais do Windows",
        "desc": "Torna a abertura e minimização de janelas instantânea.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop\WindowMetrics", "MinAnimate", winreg.REG_SZ, "0", "1"),
    },
    {
        "id": "visual.disable_transparency",
        "name": "Desativar Efeitos de Transparência (Mica/Acrylic)",
        "desc": "Reduz o consumo de GPU e VRAM na área de trabalho e barra de tarefas.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", winreg.REG_DWORD, 0, 1),
    },
    {
        "id": "visual.mouse_raw",
        "name": "Precisão do Mouse 1:1 (Desativar Aceleração do Ponteiro)",
        "desc": "Remove a curva de aceleração do Windows para mira precisa em jogos competitivos.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseSpeed", winreg.REG_SZ, "0", "1"),
    },
    {
        "id": "visual.disable_fso",
        "name": "Desativar Otimizações de Tela Inteira (FSO Global)",
        "desc": "Reduz input lag em jogos DirectX impedindo composição híbrida do DWM.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", winreg.REG_DWORD, 2, 0),
    },
    {
        "id": "visual.menu_delay_zero",
        "name": "Menu Show Delay Zero (Resposta Instantânea)",
        "desc": "Reduz o atraso de exibição de menus de contexto de 400ms para 0ms.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "MenuShowDelay", winreg.REG_SZ, "0", "400"),
    },
    {
        "id": "visual.show_extensions",
        "name": "Mostrar Extensões de Arquivos no Explorer",
        "desc": "Exibe .exe, .bat, .dll, .txt claramente para maior segurança e controle.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", winreg.REG_DWORD, 0, 1),
    },
    {
        "id": "visual.taskbar_clean",
        "name": "Ocultar Botão Visão de Tarefas e Busca na Barra",
        "desc": "Deixa a barra de tarefas limpa e reduz processos web do SearchHost.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowTaskViewButton", winreg.REG_DWORD, 0, 1),
    },
    {
        "id": "visual.disable_aero_shake",
        "name": "Desativar Aero Shake (Sacudir Janela)",
        "desc": "Evita que todas as janelas minimizem acidentalmente ao mover uma janela rápido.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\Explorer", "NoWindowMinimizingShortcuts", winreg.REG_DWORD, 1, 0),
    },
    {
        "id": "visual.disable_copilot_ai",
        "name": "Desativar Windows Copilot & Recall IA",
        "desc": "Desativa recursos de IA em segundo plano do Windows 11 para economizar RAM.",
        "risk": "Seguro",
        "reg": (winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", winreg.REG_DWORD, 1, 0),
    },
]

WINDOWS_SERVICES: List[Dict[str, str]] = [
    {
        "name": "DiagTrack",
        "display": "Experiências do Usuário Conectado e Telemetria",
        "desc": "Envia dados de diagnóstico e telemetria contínua para a Microsoft.",
        "risk": "Seguro",
    },
    {
        "name": "SysMain",
        "display": "SysMain (Superfetch)",
        "desc": "Pré-carrega apps na RAM; pode causar picos de disco/CPU em PCs com SSD.",
        "risk": "Seguro",
    },
    {
        "name": "MapsBroker",
        "display": "Gerenciador de Mapas Baixados",
        "desc": "Serviço em segundo plano para mapas offline do Windows (raramente usado).",
        "risk": "Seguro",
    },
    {
        "name": "Fax",
        "display": "Serviço de Fax do Windows",
        "desc": "Suporte legado para envio e recebimento de fax.",
        "risk": "Seguro",
    },
    {
        "name": "WpcMonSvc",
        "display": "Controle dos Pais / Segurança Familiar",
        "desc": "Monitoramento de tempo de tela familiar.",
        "risk": "Seguro",
    },
    {
        "name": "RetailDemo",
        "display": "Serviço de Demonstração de Varejo",
        "desc": "Modo de demonstração de loja física embutido no Windows.",
        "risk": "Seguro",
    },
    {
        "name": "XblGameSave",
        "display": "Salvamento de Jogos no Xbox Live",
        "desc": "Sincroniza saves da Xbox Network (desative apenas se não usar Xbox/Game Pass).",
        "risk": "Médio",
    },
    {
        "name": "WSearch",
        "display": "Windows Search (Indexador de Arquivos)",
        "desc": "Indexa arquivos constantemente em segundo plano. Desativar libera disco/CPU.",
        "risk": "Médio",
    },
    {
        "name": "Spooler",
        "display": "Spooler de Impressão",
        "desc": "Necessário apenas se você utiliza impressoras conectadas ao PC.",
        "risk": "Médio",
    },
]

POWER_PLANS: List[Dict[str, str]] = [
    {
        "id": "economia",
        "guid": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "badge": "ECO",
        "name": "Economia de Energia",
        "desc": "Maior duração de bateria em notebooks e menor aquecimento.",
    },
    {
        "id": "balanceado",
        "guid": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "badge": "AUTO",
        "name": "Equilibrado (Padrão)",
        "desc": "Ajusta a frequência do processador automaticamente conforme a demanda.",
    },
    {
        "id": "alto",
        "guid": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "badge": "ALTO",
        "name": "Alto Desempenho",
        "desc": "Prioriza desempenho mantendo clocks elevados na CPU.",
    },
    {
        "id": "ultimate",
        "guid": "e9a42b02-d5df-448d-aa00-03f14749eb61",
        "badge": "MAX PRO",
        "name": "Desempenho Máximo (Ultimate Performance)",
        "desc": "Elimina micro-latências de gerenciamento de energia para FPS estável em jogos.",
    },
]


def _run_hidden(cmd: List[str], timeout: int = 8) -> subprocess.CompletedProcess:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, startupinfo=startupinfo)


def check_visual_tweak_state(tweak: Dict[str, Any]) -> bool:
    hive, subkey, val_name, _, target_val, _ = tweak["reg"]
    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as k:
            val, _ = winreg.QueryValueEx(k, val_name)
            return str(val) == str(target_val)
    except Exception:
        return False


def apply_visual_tweak(tweak_id: str, enable: bool = True) -> Dict[str, Any]:
    tweak = next((t for t in VISUAL_TWEAKS if t["id"] == tweak_id), None)
    if not tweak:
        return {"success": False, "error": "Ajuste não encontrado."}

    hive, subkey, val_name, reg_type, on_val, off_val = tweak["reg"]
    val_to_write = on_val if enable else off_val

    try:
        with winreg.CreateKeyEx(hive, subkey, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, val_name, 0, reg_type, val_to_write)
        # Se for mouse_raw, aplica também MouseThreshold1 e MouseThreshold2 = 0
        if tweak_id == "visual.mouse_raw":
            with winreg.CreateKeyEx(hive, subkey, 0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, "MouseThreshold1", 0, winreg.REG_SZ, "0" if enable else "6")
                winreg.SetValueEx(k, "MouseThreshold2", 0, winreg.REG_SZ, "0" if enable else "10")

        logger.set_tweak_state(tweak_id, enable)
        logger.log("Otimizações", f"{'Aplicado' if enable else 'Revertido'}: {tweak['name']}", True)
        return {"success": True}
    except Exception as e:
        logger.log("Otimizações", f"Erro em {tweak['name']}", False, str(e))
        return {"success": False, "error": str(e)}


def get_services_status() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for svc in WINDOWS_SERVICES:
        status = "Stopped"
        try:
            res = _run_hidden(["sc", "query", svc["name"]], timeout=4)
            if "RUNNING" in res.stdout.upper():
                status = "Running"
        except Exception:
            pass
        results.append({**svc, "status": status})
    return results


def toggle_service(service_name: str, disable: bool) -> Dict[str, Any]:
    try:
        if disable:
            _run_hidden(["sc", "stop", service_name], timeout=6)
            res = _run_hidden(["sc", "config", service_name, "start=", "disabled"], timeout=6)
        else:
            res = _run_hidden(["sc", "config", service_name, "start=", "demand"], timeout=6)
            _run_hidden(["sc", "start", service_name], timeout=6)

        ok = res.returncode == 0
        logger.log(
            "Serviços",
            f"Serviço {service_name} {'desativado' if disable else 'reativado'}",
            ok,
            res.stderr.strip() or res.stdout.strip(),
        )
        return {"success": ok, "error": res.stderr.strip() if not ok else ""}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_active_power_plan() -> str:
    try:
        res = _run_hidden(["powercfg", "/getactivescheme"], timeout=5)
        out = res.stdout.lower()
        for plan in POWER_PLANS:
            if plan["guid"].lower() in out:
                return plan["id"]
        if "ultimate" in out or "máximo" in out:
            return "ultimate"
        if "alto" in out or "high" in out:
            return "alto"
        if "economia" in out or "saver" in out:
            return "economia"
    except Exception:
        pass
    return "balanceado"


def activate_power_plan(plan_id: str) -> Dict[str, Any]:
    plan = next((p for p in POWER_PLANS if p["id"] == plan_id), None)
    if not plan:
        return {"success": False, "error": "Plano inválido."}
    try:
        if plan_id == "ultimate":
            # Garante que o esquema Ultimate Performance esteja desbloqueado no Windows
            dup = _run_hidden(["powercfg", "-duplicatescheme", plan["guid"]], timeout=6)
            # Se retornou um novo GUID, extrai ou ativa o padrão
            res = _run_hidden(["powercfg", "/setactive", plan["guid"]], timeout=6)
            if res.returncode != 0 and dup.stdout:
                for token in dup.stdout.split():
                    if len(token) == 36 and token.count("-") == 4:
                        res = _run_hidden(["powercfg", "/setactive", token], timeout=6)
                        break
        else:
            res = _run_hidden(["powercfg", "/setactive", plan["guid"]], timeout=6)

        ok = res.returncode == 0
        logger.set_tweak_state(f"power.{plan_id}", ok)
        logger.log("Energia", f"Plano ativado: {plan['name']}", ok)
        return {"success": ok, "error": res.stderr.strip() if not ok else ""}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_startup_items() -> List[Dict[str, Any]]:
    """Lista programas configurados na inicialização do usuário e do sistema."""
    items: List[Dict[str, Any]] = []
    locations = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "Usuário (HKCU)"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "Sistema (HKLM)"),
    ]
    for hive, subkey, source_label in locations:
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as k:
                idx = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(k, idx)
                        items.append({
                            "name": name,
                            "path": str(value),
                            "source": source_label,
                            "hive": "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM",
                            "enabled": True,
                            "impact": "Alto" if any(x in str(value).lower() for x in ["steam", "discord", "epic", "adobe", "teams", "spotify"]) else "Médio",
                        })
                        idx += 1
                    except OSError:
                        break
        except Exception:
            pass
    return items


def remove_startup_item(name: str, hive_str: str = "HKCU") -> Dict[str, Any]:
    hive = winreg.HKEY_CURRENT_USER if hive_str == "HKCU" else winreg.HKEY_LOCAL_MACHINE
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, name)
        logger.log("Inicialização", f"Removido da inicialização: {name}", True)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_installed_apps(max_count: int = 80) -> List[Dict[str, str]]:
    """Lista programas instalados a partir do Registro do Windows."""
    apps: List[Dict[str, str]] = []
    seen = set()
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, path in reg_paths:
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as k:
                for i in range(winreg.QueryInfoKey(k)[0]):
                    try:
                        sub_name = winreg.EnumKey(k, i)
                        with winreg.OpenKey(k, sub_name) as sub_k:
                            name, _ = winreg.QueryValueEx(sub_k, "DisplayName")
                            name_str = str(name).strip()
                            if not name_str or name_str in seen:
                                continue
                            publisher = ""
                            version = ""
                            uninstall = ""
                            try:
                                publisher = str(winreg.QueryValueEx(sub_k, "Publisher")[0])
                            except Exception:
                                pass
                            try:
                                version = str(winreg.QueryValueEx(sub_k, "DisplayVersion")[0])
                            except Exception:
                                pass
                            try:
                                uninstall = str(winreg.QueryValueEx(sub_k, "UninstallString")[0])
                            except Exception:
                                pass
                            seen.add(name_str)
                            apps.append({
                                "name": name_str,
                                "publisher": publisher or "Desconhecido",
                                "version": version or "-",
                                "uninstall": uninstall,
                            })
                    except Exception:
                        pass
        except Exception:
            pass

    apps.sort(key=lambda x: x["name"].lower())
    return apps[:max_count]
