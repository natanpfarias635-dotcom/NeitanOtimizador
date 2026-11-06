# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Catálogo de Perfis & Otimização em 1 Clique (Wizard)
Todos os perfis PRO do OtimizePC liberados gratuitamente.
"""

from typing import Any, Dict, List

from src.core.cleanup_engine import run_cleanup
from src.core.gaming_engine import apply_gaming_tweak, flush_ram_working_sets
from src.core.logger import logger
from src.core.network_engine import apply_network_tweak
from src.core.optimizer_engine import activate_power_plan, apply_visual_tweak
from src.core.privacy_engine import apply_privacy_item

PROFILES: List[Dict[str, Any]] = [
    {
        "id": "gamer_competitivo",
        "badge": "RECOMENDADO · FPS MÁXIMO",
        "name": "Gamer Competitivo (E-Sports)",
        "desc": "Foco absoluto em reduzir Input Lag, estabilizar 1% Low FPS, ativar Ultimate Performance, Mouse Raw 1:1 e Rede Gaming.",
        "gain_estimate": "+8% a +18% em estabilidade de FPS (1% Low)",
        "power_plan": "ultimate",
        "visual": ["visual.disable_animations", "visual.disable_transparency", "visual.mouse_raw", "visual.disable_fso", "visual.menu_delay_zero"],
        "gaming": ["gaming.hags", "gaming.mmcss_timer", "gaming.game_mode", "gaming.power_throttling_off"],
        "network": ["dns_gaming", "qos_limit_zero", "network_throttling_off", "tcp_gaming_tuning"],
        "privacy": ["privacy.telemetry", "privacy.bing_search", "privacy.widgets_off", "privacy.gamebar_dvr_off"],
    },
    {
        "id": "gamer_streamer",
        "badge": "STREAM & CRIAÇÃO",
        "name": "Gamer + Streamer (OBS / Multitarefa)",
        "desc": "Alta performance em jogos preservando codificação NVENC/AMF, captura de janela e estabilidade de rede para lives.",
        "gain_estimate": "Zero perda de quadros no OBS + menor latência",
        "power_plan": "alto",
        "visual": ["visual.mouse_raw", "visual.menu_delay_zero", "visual.show_extensions", "visual.disable_copilot_ai"],
        "gaming": ["gaming.mmcss_timer", "gaming.game_mode", "gaming.power_throttling_off"],
        "network": ["dns_gaming", "qos_limit_zero", "tcp_gaming_tuning", "delivery_opt_off"],
        "privacy": ["privacy.advertising_id", "privacy.telemetry", "privacy.consumer_features", "privacy.feedback_off"],
    },
    {
        "id": "trabalho_produtividade",
        "badge": "WORKSTATION",
        "name": "Trabalho & Produtividade Ágil",
        "desc": "Deixa o Windows extremamente responsivo para programação, edição, navegação intensa e inicialização rápida.",
        "gain_estimate": "Abertura de janelas e menus até 2x mais ágil",
        "power_plan": "alto",
        "visual": ["visual.menu_delay_zero", "visual.show_extensions", "visual.disable_aero_shake", "visual.disable_copilot_ai"],
        "gaming": ["gaming.power_throttling_off"],
        "network": ["dns_gaming", "delivery_opt_off"],
        "privacy": ["privacy.advertising_id", "privacy.bing_search", "privacy.telemetry", "privacy.consumer_features", "privacy.feedback_off"],
    },
    {
        "id": "notebook_eficiencia",
        "badge": "NOTEBOOK & BATERIA",
        "name": "Notebook Equilibrado & Silencioso",
        "desc": "Remove telemetria, widgets e processos ociosos que drenam bateria e aquecem o notebook.",
        "gain_estimate": "Menor uso de CPU em repouso e menor temperatura",
        "power_plan": "balanceado",
        "visual": ["visual.disable_transparency", "visual.taskbar_clean", "visual.disable_copilot_ai"],
        "gaming": ["gaming.game_mode"],
        "network": ["delivery_opt_off"],
        "privacy": ["privacy.advertising_id", "privacy.bing_search", "privacy.telemetry", "privacy.activity_history", "privacy.widgets_off"],
    },
    {
        "id": "neitan_ultra_red",
        "badge": "NEITAN EXTREME PRO",
        "name": "Neitan Ultra Red (Desempenho Extremo)",
        "desc": "Aplica TODOS os ajustes de performance, visual, jogos, rede e privacidade simultaneamente.",
        "gain_estimate": "Performance máxima liberada em todas as camadas",
        "power_plan": "ultimate",
        "visual": [
            "visual.disable_animations",
            "visual.disable_transparency",
            "visual.mouse_raw",
            "visual.disable_fso",
            "visual.menu_delay_zero",
            "visual.show_extensions",
            "visual.taskbar_clean",
            "visual.disable_aero_shake",
            "visual.disable_copilot_ai",
        ],
        "gaming": ["gaming.hags", "gaming.mmcss_timer", "gaming.game_mode", "gaming.power_throttling_off"],
        "network": ["dns_gaming", "qos_limit_zero", "network_throttling_off", "tcp_gaming_tuning", "delivery_opt_off"],
        "privacy": [
            "privacy.advertising_id",
            "privacy.bing_search",
            "privacy.telemetry",
            "privacy.activity_history",
            "privacy.consumer_features",
            "privacy.feedback_off",
            "privacy.widgets_off",
            "privacy.gamebar_dvr_off",
        ],
    },
]


def apply_profile(profile_id: str) -> Dict[str, Any]:
    profile = next((p for p in PROFILES if p["id"] == profile_id), None)
    if not profile:
        return {"success": False, "error": "Perfil não encontrado."}

    applied_items: List[str] = []
    failed = 0

    if profile.get("power_plan"):
        res = activate_power_plan(profile["power_plan"])
        if res.get("success"):
            applied_items.append(f"power.{profile['power_plan']}")
        else:
            failed += 1

    for vid in profile.get("visual", []):
        if apply_visual_tweak(vid, True).get("success"):
            applied_items.append(vid)
        else:
            failed += 1

    for gid in profile.get("gaming", []):
        if apply_gaming_tweak(gid, True).get("success"):
            applied_items.append(gid)
        else:
            failed += 1

    for nid in profile.get("network", []):
        if apply_network_tweak(nid, True).get("success"):
            applied_items.append(f"net.{nid}")
        else:
            failed += 1

    for pid in profile.get("privacy", []):
        if apply_privacy_item(pid, True).get("success"):
            applied_items.append(pid)
        else:
            failed += 1

    logger.set_tweak_state(f"profile.{profile_id}", True, active_profile=profile["name"])
    session = logger.record_session(profile_id, profile["name"], applied_items, failed)
    return {
        "success": True,
        "profile_name": profile["name"],
        "applied_count": len(applied_items),
        "failed_count": failed,
        "session_id": session["sessionId"],
    }


def revert_session(session_id: str) -> Dict[str, Any]:
    sessions = logger.get_sessions()
    sess = next((s for s in sessions if s["sessionId"] == session_id), None)
    if not sess:
        return {"success": False, "error": "Sessão não encontrada."}

    reverted = 0
    for item_id in sess.get("items", []):
        if item_id.startswith("visual."):
            if apply_visual_tweak(item_id, False).get("success"):
                reverted += 1
        elif item_id.startswith("gaming."):
            if apply_gaming_tweak(item_id, False).get("success"):
                reverted += 1
        elif item_id.startswith("net."):
            if apply_network_tweak(item_id.replace("net.", ""), False).get("success"):
                reverted += 1
        elif item_id.startswith("privacy."):
            if apply_privacy_item(item_id, False).get("success"):
                reverted += 1
        elif item_id.startswith("power."):
            if activate_power_plan("balanceado").get("success"):
                reverted += 1

    logger.log("Histórico", f"Sessão {session_id} revertida ({sess.get('profileName')})", True, f"{reverted} ajustes restaurados ao padrão")
    return {"success": True, "reverted_count": reverted}


def run_one_click_wizard() -> Dict[str, Any]:
    """Executa o 'Otimizar em 1 Clique': Limpeza Básica + RAM Flush + Perfil Gamer Competitivo."""
    clean_res = run_cleanup(["temp", "browsers", "logs", "prefetch", "shadercache", "appcache"])
    ram_res = flush_ram_working_sets()
    prof_res = apply_profile("gamer_competitivo")

    logger.log(
        "1-Clique",
        "Otimização Completa em 1 Clique executada",
        True,
        f"Limpeza: {clean_res.get('freed_formatted')} | RAM: +{ram_res.get('freed_mb', 0)} MB | Ajustes: {prof_res.get('applied_count', 0)}",
    )
    return {
        "success": True,
        "freed_disk": clean_res.get("freed_formatted", "0 MB"),
        "freed_ram_mb": ram_res.get("freed_mb", 0),
        "applied_tweaks": prof_res.get("applied_count", 0),
        "profile_name": prof_res.get("profile_name", "Gamer Competitivo"),
    }
