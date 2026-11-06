# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Motor de Privacidade e Anti-Telemetria (Individual e em Lote)
Baseado na aba Privacidade do OtimizePC, 100% liberado.
"""

import winreg
from typing import Any, Dict, List

from src.core.logger import logger

PRIVACY_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "privacy.advertising_id",
        "name": "Desativar ID de Anúncio e Rastreamento Publicitário",
        "desc": "Impede que aplicativos usem seu identificador único para anúncios personalizados.",
        "risk": "Seguro",
        "hive": winreg.HKEY_CURRENT_USER,
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
        "value_name": "Enabled",
        "on_value": 0,
        "off_value": 1,
    },
    {
        "id": "privacy.bing_search",
        "name": "Desativar Busca Web do Bing no Menu Iniciar",
        "desc": "Deixa a pesquisa do Menu Iniciar instantânea e 100% local, sem enviar o que você digita ao Bing.",
        "risk": "Seguro",
        "hive": winreg.HKEY_CURRENT_USER,
        "subkey": r"Software\Policies\Microsoft\Windows\Explorer",
        "value_name": "DisableSearchBoxSuggestions",
        "on_value": 1,
        "off_value": 0,
    },
    {
        "id": "privacy.telemetry",
        "name": "Reduzir Telemetria e Coleta de Diagnóstico ao Mínimo",
        "desc": "Configura AllowTelemetry=0 nas políticas do Windows para bloquear coleta de dados.",
        "risk": "Seguro",
        "hive": winreg.HKEY_LOCAL_MACHINE,
        "subkey": r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
        "value_name": "AllowTelemetry",
        "on_value": 0,
        "off_value": 1,
    },
    {
        "id": "privacy.activity_history",
        "name": "Bloquear Histórico de Atividades e Linha do Tempo",
        "desc": "Impede o Windows de gravar e sincronizar histórico de arquivos e aplicativos abertos.",
        "risk": "Seguro",
        "hive": winreg.HKEY_LOCAL_MACHINE,
        "subkey": r"SOFTWARE\Policies\Microsoft\Windows\System",
        "value_name": "PublishUserActivities",
        "on_value": 0,
        "off_value": 1,
    },
    {
        "id": "privacy.consumer_features",
        "name": "Bloquear Instalação Automática de Apps Sugeridos (Bloatware)",
        "desc": "Evita que o Windows instale jogos e apps patrocinados silenciosamente.",
        "risk": "Seguro",
        "hive": winreg.HKEY_CURRENT_USER,
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
        "value_name": "SilentInstalledAppsEnabled",
        "on_value": 0,
        "off_value": 1,
    },
    {
        "id": "privacy.feedback_off",
        "name": "Desativar Solicitações Automáticas de Feedback do Windows",
        "desc": "Zera a frequência de pop-ups pedindo avaliação de uso do sistema.",
        "risk": "Seguro",
        "hive": winreg.HKEY_CURRENT_USER,
        "subkey": r"Software\Microsoft\Siuf\Rules",
        "value_name": "NumberOfSIUFInPeriod",
        "on_value": 0,
        "off_value": 1,
    },
    {
        "id": "privacy.widgets_off",
        "name": "Desativar Painel de Notícias e Widgets da Barra de Tarefas",
        "desc": "Encerra o consumo de RAM/Rede do WebView2 usado pelo painel de Widgets.",
        "risk": "Seguro",
        "hive": winreg.HKEY_CURRENT_USER,
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "value_name": "TaskbarDa",
        "on_value": 0,
        "off_value": 1,
    },
    {
        "id": "privacy.gamebar_dvr_off",
        "name": "Desativar Gravação em Segundo Plano (Xbox Game DVR)",
        "desc": "Impede gravação contínua de tela em segundo plano que reduz o FPS.",
        "risk": "Moderado",
        "hive": winreg.HKEY_CURRENT_USER,
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\GameDVR",
        "value_name": "AppCaptureEnabled",
        "on_value": 0,
        "off_value": 1,
    },
]


def check_privacy_item(item: Dict[str, Any]) -> bool:
    try:
        with winreg.OpenKey(item["hive"], item["subkey"], 0, winreg.KEY_READ) as k:
            val, _ = winreg.QueryValueEx(k, item["value_name"])
            return int(val) == int(item["on_value"])
    except Exception:
        return False


def apply_privacy_item(item_id: str, enable: bool = True) -> Dict[str, Any]:
    item = next((i for i in PRIVACY_ITEMS if i["id"] == item_id), None)
    if not item:
        return {"success": False, "error": "Item de privacidade não encontrado."}

    val = item["on_value"] if enable else item["off_value"]
    try:
        with winreg.CreateKeyEx(item["hive"], item["subkey"], 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, item["value_name"], 0, winreg.REG_DWORD, val)
        logger.set_tweak_state(item_id, enable)
        logger.log("Privacidade", f"{'Aplicado' if enable else 'Revertido'}: {item['name']}", True)
        return {"success": True}
    except Exception as e:
        logger.log("Privacidade", f"Falha em {item['name']}", False, str(e))
        return {"success": False, "error": str(e)}


def apply_all_privacy(enable: bool = True) -> Dict[str, Any]:
    ok_count = 0
    for item in PRIVACY_ITEMS:
        res = apply_privacy_item(item["id"], enable)
        if res.get("success"):
            ok_count += 1
    return {"success": ok_count > 0, "applied": ok_count, "total": len(PRIVACY_ITEMS)}
