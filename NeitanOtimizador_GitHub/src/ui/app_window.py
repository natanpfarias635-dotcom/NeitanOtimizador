# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Janela Principal CustomTkinter (Paleta Vermelho & Preto)
Todas as funções do modelo OtimizePC 100% desbloqueadas.
"""

import os
import subprocess
import threading
from typing import Dict
import customtkinter as ctk

from src.theme import APP_NAME, APP_SUBTITLE, APP_VERSION, COLORS, FONTS
from src.ui.components import MetricCard, PageHeader, SubTabBar
from src.core.logger import logger
from src.core.system_monitor import (
    get_hardware_summary,
    get_live_metrics,
    get_winsat_scores,
    is_user_admin,
)
from src.core.cleanup_engine import (
    CLEANUP_ITEMS,
    format_bytes,
    measure_cleanup_sizes,
    run_cleanup,
    scan_duplicate_files,
    scan_large_files,
)
from src.core.optimizer_engine import (
    POWER_PLANS,
    VISUAL_TWEAKS,
    activate_power_plan,
    apply_visual_tweak,
    check_visual_tweak_state,
    get_active_power_plan,
    get_services_status,
    list_installed_apps,
    list_startup_items,
    remove_startup_item,
    toggle_service,
)
from src.core.gaming_engine import (
    GAMING_TWEAKS,
    apply_all_gaming_tweaks,
    apply_gaming_tweak,
    check_gaming_tweak,
    detect_game_libraries,
    flush_ram_working_sets,
    run_game_session_boost,
)
from src.core.network_engine import (
    NETWORK_TWEAKS,
    apply_network_tweak,
    get_network_overview,
    reset_network_stack,
    run_dns_benchmark,
    run_stability_test,
)
from src.core.privacy_engine import (
    PRIVACY_ITEMS,
    apply_all_privacy,
    apply_privacy_item,
    check_privacy_item,
)
from src.core.profiles_engine import (
    PROFILES,
    apply_profile,
    revert_session,
    run_one_click_wizard,
)
from src.core.updates_scheduler import (
    check_winget_updates,
    create_restore_point,
    delete_schedule,
    get_schedules,
    list_restore_points,
    open_windows_restore_ui,
    save_schedule,
    upgrade_all_winget,
)


class NeitanOtimizadorApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title(f"{APP_NAME} — {APP_VERSION}")
        self.geometry("1240x780")
        self.minsize(1040, 680)
        self.configure(fg_color=COLORS["bg_main"])

        try:
            from pathlib import Path
            import sys
            base_p = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent.parent))
            ico_file = base_p / "assets" / "neitan_icon.ico"
            if ico_file.exists():
                self.iconbitmap(str(ico_file))
        except Exception:
            pass

        self.is_admin = is_user_admin()
        self.hw_info = {"cpu": "Detectando...", "gpu": "Detectando...", "ram": "--", "os": "Windows"}
        self.cleanup_vars: Dict[str, ctk.BooleanVar] = {}
        self.cleanup_size_labels: Dict[str, ctk.CTkLabel] = {}
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        self.current_page = "painel"

        self._build_layout()
        self.show_page("painel")

        # Traz a janela para frente ao abrir
        self.lift()
        self.attributes("-topmost", True)
        self.after(600, lambda: self.attributes("-topmost", False))
        self.focus_force()

        # Carrega informações de hardware em background
        threading.Thread(target=self._load_hardware_bg, daemon=True).start()
        # Loop de monitoramento ao vivo
        self.after(800, self._update_live_monitor)

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==================== SIDEBAR (PRETO & VERMELHO) ====================
        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=0,
            fg_color=COLORS["bg_sidebar"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Brand Header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(18, 12))

        logo_badge = ctk.CTkFrame(
            brand_frame,
            width=38,
            height=38,
            corner_radius=10,
            fg_color=COLORS["red_primary"],
        )
        logo_badge.pack(side="left", padx=(0, 10))
        logo_badge.pack_propagate(False)
        ctk.CTkLabel(
            logo_badge,
            text="N",
            font=("Segoe UI", 20, "bold"),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.5, anchor="center")

        title_col = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            title_col,
            text="NEITAN",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            title_col,
            text="OTIMIZADOR PRO",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["red_bright"],
            anchor="w",
        ).pack(fill="x")

        # Botão Destaque: Otimizar em 1 Clique
        self.oneclick_btn = ctk.CTkButton(
            self.sidebar,
            text="⚡ Otimizar em 1 Clique",
            height=42,
            corner_radius=10,
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            text_color="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
            command=self._trigger_one_click_wizard,
        )
        self.oneclick_btn.pack(fill="x", padx=14, pady=(0, 12))

        # Itens de Navegação (Todas as abas do OtimizePC, sem cadeados!)
        nav_items = [
            ("painel", "📊  Painel Geral"),
            ("perfis", "🎯  Perfis de Otimização"),
            ("limpeza", "🧹  Limpeza Profunda"),
            ("otimizacoes", "🚀  Otimizações do Sistema"),
            ("jogos", "🎮  Jogos & Game Boost"),
            ("rede", "🌐  Rede & Ping Gamer"),
            ("privacidade", "🛡️  Privacidade & Telemetria"),
            ("atualizacoes", "🔄  Atualizações & WinSAT"),
            ("agendar", "⏰  Agendador Automático"),
            ("historico", "📜  Histórico & Restauração"),
        ]

        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, padx=10)

        for page_id, label in nav_items:
            btn = ctk.CTkButton(
                nav_container,
                text=label,
                anchor="w",
                height=37,
                corner_radius=8,
                font=FONTS["body_bold"],
                fg_color="transparent",
                hover_color=COLORS["bg_card_hover"],
                text_color=COLORS["text_secondary"],
                command=lambda pid=page_id: self.show_page(pid),
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[page_id] = btn

        # Rodapé da Sidebar (Status Admin + Edição Desbloqueada)
        footer = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border_red"],
        )
        footer.pack(fill="x", padx=12, pady=14)

        admin_txt = "● MODO ADMINISTRADOR ATIVO" if self.is_admin else "⚠ MODO USUÁRIO PADRÃO"
        admin_col = COLORS["ok"] if self.is_admin else COLORS["warn"]
        ctk.CTkLabel(
            footer,
            text=admin_txt,
            font=("Segoe UI", 10, "bold"),
            text_color=admin_col,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            footer,
            text="Licença: Vitalícia Desbloqueada\nSem limites · Todos os recursos PRO",
            font=("Segoe UI", 10),
            text_color=COLORS["text_secondary"],
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 10))

        # ==================== ÁREA PRINCIPAL ====================
        self.main_wrapper = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        self.main_wrapper.grid(row=0, column=1, sticky="nsew")
        self.main_wrapper.grid_rowconfigure(1, weight=1)
        self.main_wrapper.grid_columnconfigure(0, weight=1)

        # Barra de Notificação / Status no Topo
        self.status_banner = ctk.CTkFrame(
            self.main_wrapper,
            height=36,
            fg_color=COLORS["bg_surface"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.status_banner.grid(row=0, column=0, sticky="ew")
        self.status_label = ctk.CTkLabel(
            self.status_banner,
            text=f"🔥 Bem-vindo ao {APP_NAME} — Todos os módulos de alta performance estão liberados.",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self.status_label.pack(side="left", padx=20, pady=6)

        # Container rolável onde as páginas são renderizadas
        self.page_scroll = ctk.CTkScrollableFrame(
            self.main_wrapper,
            fg_color=COLORS["bg_main"],
            corner_radius=0,
            scrollbar_button_color=COLORS["red_dark"],
            scrollbar_button_hover_color=COLORS["red_primary"],
        )
        self.page_scroll.grid(row=1, column=0, sticky="nsew", padx=22, pady=16)
        self.page_scroll.grid_columnconfigure(0, weight=1)

    def notify(self, message: str, tone: str = "info") -> None:
        color_map = {
            "ok": COLORS["ok"],
            "warn": COLORS["warn"],
            "bad": COLORS["bad"],
            "info": COLORS["red_bright"],
        }
        self.status_label.configure(text=message, text_color=color_map.get(tone, COLORS["text_primary"]))

    def _load_hardware_bg(self) -> None:
        self.hw_info = get_hardware_summary()

    def _update_live_monitor(self) -> None:
        if self.current_page == "painel" and hasattr(self, "cpu_card"):
            m = get_live_metrics()
            try:
                self.cpu_card.update_metric(
                    f"{m['cpu_percent']}%",
                    m["cpu_percent"] / 100.0,
                    f"Processos ativos: {m['process_count']} · Ligado há {m['uptime_str']}",
                )
                self.ram_card.update_metric(
                    f"{m['ram_percent']}%",
                    m["ram_percent"] / 100.0,
                    f"{m['ram_used_gb']} GB usados de {m['ram_total_gb']} GB",
                )
                self.disk_card.update_metric(
                    f"{m['disk_percent']}%",
                    m["disk_percent"] / 100.0,
                    f"Livre: {m['disk_free_gb']} GB de {m['disk_total_gb']} GB",
                )
                self.health_score_lbl.configure(text=f"{m['health_score']}/100")
                self.health_status_lbl.configure(
                    text=m["health_label"],
                    text_color=COLORS["ok"] if m["health_score"] >= 75 else COLORS["warn"],
                )
                if hasattr(self, "hw_summary_lbl"):
                    self.hw_summary_lbl.configure(
                        text=f"CPU: {self.hw_info['cpu']}   |   GPU: {self.hw_info['gpu']}   |   {self.hw_info['ram']}"
                    )
            except Exception:
                pass
        self.after(2000, self._update_live_monitor)

    def _clear_page(self) -> None:
        for child in self.page_scroll.winfo_children():
            child.destroy()

    def show_page(self, page_id: str) -> None:
        self.current_page = page_id
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=COLORS["red_muted_bg"],
                    text_color=COLORS["red_bright"],
                    border_width=1,
                    border_color=COLORS["red_primary"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    border_width=0,
                )

        self._clear_page()
        builders = {
            "painel": self._build_painel_page,
            "perfis": self._build_perfis_page,
            "limpeza": self._build_limpeza_page,
            "otimizacoes": self._build_otimizacoes_page,
            "jogos": self._build_jogos_page,
            "rede": self._build_rede_page,
            "privacidade": self._build_privacidade_page,
            "atualizacoes": self._build_atualizacoes_page,
            "agendar": self._build_agendar_page,
            "historico": self._build_historico_page,
        }
        builder = builders.get(page_id, self._build_painel_page)
        builder()

    # =========================================================================
    # AÇÃO RÁPIDA: OTIMIZAR EM 1 CLIQUE
    # =========================================================================
    def _trigger_one_click_wizard(self) -> None:
        self.oneclick_btn.configure(state="disabled", text="⏳ Otimizando PC...")
        self.notify("⚡ Executando Otimização em 1 Clique (Limpeza + RAM Flush + Perfil Gamer Competitivo)...", "info")

        def _worker():
            res = run_one_click_wizard()
            self.after(0, lambda: self._on_one_click_done(res))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_one_click_done(self, res: Dict) -> None:
        self.oneclick_btn.configure(state="normal", text="⚡ Otimizar em 1 Clique")
        msg = (
            f"✓ Otimização 1-Clique concluída! Disco liberado: {res.get('freed_disk')} | "
            f"RAM liberada: +{res.get('freed_ram_mb')} MB | {res.get('applied_tweaks')} ajustes aplicados."
        )
        self.notify(msg, "ok")
        if self.current_page == "painel":
            self.show_page("painel")

    # =========================================================================
    # 1. PÁGINA: PAINEL (DASHBOARD)
    # =========================================================================
    def _build_painel_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="📊",
            kicker="Monitoramento em Tempo Real",
            title=f"Painel de Controle · {APP_NAME}",
            subtitle="Visão ao vivo de CPU, Memória RAM, Disco, Saúde do Sistema e Otimizações Aplicadas.",
        ).pack(fill="x", pady=(0, 14))

        # Banner de Hardware Detectado
        hw_bar = ctk.CTkFrame(
            self.page_scroll,
            fg_color=COLORS["bg_card_alt"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border_red"],
        )
        hw_bar.pack(fill="x", pady=(0, 14))
        self.hw_summary_lbl = ctk.CTkLabel(
            hw_bar,
            text=f"CPU: {self.hw_info['cpu']}   |   GPU: {self.hw_info['gpu']}   |   {self.hw_info['ram']}",
            font=FONTS["small"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.hw_summary_lbl.pack(fill="x", padx=16, pady=10)

        # Grid de 4 Cards de Métricas
        metrics_grid = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        metrics_grid.pack(fill="x", pady=(0, 16))
        for col in range(4):
            metrics_grid.grid_columnconfigure(col, weight=1)

        m = get_live_metrics()
        self.cpu_card = MetricCard(
            metrics_grid,
            "Uso de CPU",
            f"{m['cpu_percent']}%",
            f"Processos: {m['process_count']} · Uptime: {m['uptime_str']}",
        )
        self.cpu_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        self.ram_card = MetricCard(
            metrics_grid,
            "Memória RAM",
            f"{m['ram_percent']}%",
            f"{m['ram_used_gb']} GB / {m['ram_total_gb']} GB",
        )
        self.ram_card.grid(row=0, column=1, padx=8, sticky="nsew")

        self.disk_card = MetricCard(
            metrics_grid,
            "Disco Principal (C:)",
            f"{m['disk_percent']}%",
            f"Livre: {m['disk_free_gb']} GB de {m['disk_total_gb']} GB",
        )
        self.disk_card.grid(row=0, column=2, padx=8, sticky="nsew")

        # Card de Saúde Geral
        health_card = ctk.CTkFrame(
            metrics_grid,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["red_border"],
        )
        health_card.grid(row=0, column=3, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(
            health_card,
            text="ÍNDICE DE SAÚDE",
            font=FONTS["kicker"],
            text_color=COLORS["red_bright"],
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 2))
        self.health_score_lbl = ctk.CTkLabel(
            health_card,
            text=f"{m['health_score']}/100",
            font=FONTS["metric"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.health_score_lbl.pack(fill="x", padx=16, pady=(0, 4))
        self.health_status_lbl = ctk.CTkLabel(
            health_card,
            text=m["health_label"],
            font=FONTS["body_bold"],
            text_color=COLORS["ok"],
            anchor="w",
        )
        self.health_status_lbl.pack(fill="x", padx=16, pady=(0, 14))

        # Seção: Ações Rápidas & Status do Sistema
        row2 = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 14))
        row2.grid_columnconfigure(0, weight=3)
        row2.grid_columnconfigure(1, weight=2)

        # Card CTA Otimização Rápida
        cta_card = ctk.CTkFrame(
            row2,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        cta_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(
            cta_card,
            text="CENTRAL DE AÇÃO RÁPIDA NEITAN",
            font=FONTS["kicker"],
            text_color=COLORS["red_bright"],
            anchor="w",
        ).pack(fill="x", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            cta_card,
            text="Seu computador pronto para máximo FPS e zero engasgos",
            font=FONTS["title_md"],
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 6))
        ctk.CTkLabel(
            cta_card,
            text="Execute o diagnóstico ou aplique diretamente os módulos de limpeza, liberação de RAM, DNS Gamer e Plano de Energia Ultimate Performance.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            wraplength=580,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 14))

        btn_bar = ctk.CTkFrame(cta_card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=18, pady=(0, 16))

        ctk.CTkButton(
            btn_bar,
            text="⚡ Otimizar Tudo em 1 Clique",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            font=FONTS["body_bold"],
            height=38,
            command=self._trigger_one_click_wizard,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_bar,
            text="🚀 Liberar Memória RAM Agora",
            fg_color=COLORS["bg_surface"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["red_border"],
            font=FONTS["body_bold"],
            height=38,
            command=self._quick_ram_flush,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_bar,
            text="🎯 Escolher Perfil",
            fg_color=COLORS["bg_surface"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            font=FONTS["body_bold"],
            height=38,
            command=lambda: self.show_page("perfis"),
        ).pack(side="left")

        # Card Resumo de Sessão / Estado Aplicado
        state = logger.get_applied_state()
        applied_count = sum(1 for v in state.get("tweaks", {}).values() if v)
        active_prof = state.get("active_profile") or "Personalizado / Nenhum perfil fixo"
        last_opt = state.get("last_opt") or "Nenhuma otimização registrada ainda"

        status_card = ctk.CTkFrame(
            row2,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        status_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(
            status_card,
            text="STATUS DAS OTIMIZAÇÕES",
            font=FONTS["kicker"],
            text_color=COLORS["red_bright"],
            anchor="w",
        ).pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(
            status_card,
            text=f"Perfil Ativo: {active_prof}",
            font=FONTS["title_sm"],
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 4))

        ctk.CTkLabel(
            status_card,
            text=f"Ajustes ativos registrados: {applied_count}\nÚltima execução: {last_opt}\nPlano de Energia atual: {get_active_power_plan().upper()}",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 16))

    def _quick_ram_flush(self) -> None:
        res = flush_ram_working_sets()
        self.notify(
            f"✓ Memória RAM otimizada! {res.get('trimmed_processes', 0)} processos limpos (+{res.get('freed_mb', 0)} MB livres).",
            "ok",
        )

    # =========================================================================
    # 2. PÁGINA: PERFIS DE OTIMIZAÇÃO
    # =========================================================================
    def _build_perfis_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="🎯",
            kicker="Catálogo de Perfis Pré-Configurados",
            title="Perfis de Otimização Neitan",
            subtitle="Aplique pacotes completos de ajustes calibrados para o seu estilo de uso com reversão garantida.",
        ).pack(fill="x", pady=(0, 14))

        for prof in PROFILES:
            card = ctk.CTkFrame(
                self.page_scroll,
                fg_color=COLORS["bg_card"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["red_border"] if prof["id"] in ("gamer_competitivo", "neitan_ultra_red") else COLORS["border"],
            )
            card.pack(fill="x", pady=6)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=18, pady=(14, 4))

            badge = ctk.CTkLabel(
                top,
                text=prof["badge"],
                font=("Segoe UI", 10, "bold"),
                text_color=COLORS["red_bright"],
                fg_color=COLORS["red_dark"],
                corner_radius=6,
                padx=8,
                pady=2,
            )
            badge.pack(side="left")

            gain_lbl = ctk.CTkLabel(
                top,
                text=f"⚡ Estimativa: {prof['gain_estimate']}",
                font=FONTS["small"],
                text_color=COLORS["ok"],
            )
            gain_lbl.pack(side="right")

            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(fill="x", padx=18, pady=(2, 14))

            info_col = ctk.CTkFrame(body, fg_color="transparent")
            info_col.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                info_col,
                text=prof["name"],
                font=FONTS["title_md"],
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(fill="x")

            ctk.CTkLabel(
                info_col,
                text=prof["desc"],
                font=FONTS["body"],
                text_color=COLORS["text_secondary"],
                anchor="w",
                wraplength=680,
                justify="left",
            ).pack(fill="x", pady=(2, 6))

            total_items = (
                1
                + len(prof["visual"])
                + len(prof["gaming"])
                + len(prof["network"])
                + len(prof["privacy"])
            )
            ctk.CTkLabel(
                info_col,
                text=f"Inclui {total_items} ajustes combinados: Energia ({prof['power_plan'].upper()}) · {len(prof['visual'])} Visuais · {len(prof['gaming'])} Gaming · {len(prof['network'])} Rede · {len(prof['privacy'])} Privacidade",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
                anchor="w",
            ).pack(fill="x")

            ctk.CTkButton(
                body,
                text="Aplicar Perfil →",
                fg_color=COLORS["red_primary"],
                hover_color=COLORS["red_hover"],
                font=FONTS["body_bold"],
                width=150,
                height=38,
                command=lambda pid=prof["id"]: self._apply_selected_profile(pid),
            ).pack(side="right", padx=(16, 0))

    def _apply_selected_profile(self, profile_id: str) -> None:
        self.notify("⏳ Aplicando perfil de otimização...", "info")

        def _worker():
            res = apply_profile(profile_id)
            self.after(
                0,
                lambda: self.notify(
                    f"✓ Perfil '{res.get('profile_name')}' aplicado com sucesso! ({res.get('applied_count')} ajustes ativos · Sessão {res.get('session_id')})",
                    "ok",
                ),
            )

        threading.Thread(target=_worker, daemon=True).start()

    # =========================================================================
    # 3. PÁGINA: LIMPEZA PROFUNDA (3 SUB-ABAS)
    # =========================================================================
    def _build_limpeza_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="🧹",
            kicker="Desobstrução de Armazenamento & Cache",
            title="Limpeza Básica & Avançada",
            subtitle="Remova arquivos temporários, caches de shaders/navegadores, ou localize arquivos gigantes e duplicados.",
        ).pack(fill="x", pady=(0, 12))

        self.limpeza_content = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        SubTabBar(
            self.page_scroll,
            tabs=[
                ("cleanup", "🧹 Limpeza de Sistema & Shaders"),
                ("large", "📦 Scanner de Arquivos Grandes"),
                ("duplicates", "📑 Scanner de Arquivos Duplicados"),
            ],
            on_select=self._render_limpeza_subtab,
            initial="cleanup",
        ).pack(fill="x", pady=(0, 12))
        self.limpeza_content.pack(fill="both", expand=True)
        self._render_limpeza_subtab("cleanup")

    def _render_limpeza_subtab(self, tab_id: str) -> None:
        for w in self.limpeza_content.winfo_children():
            w.destroy()

        if tab_id == "cleanup":
            cols = ctk.CTkFrame(self.limpeza_content, fg_color="transparent")
            cols.pack(fill="x", pady=(0, 12))
            cols.grid_columnconfigure(0, weight=1)
            cols.grid_columnconfigure(1, weight=1)

            basic_card = ctk.CTkFrame(cols, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            basic_card.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
            ctk.CTkLabel(basic_card, text="LIMPEZA BÁSICA (USO DIÁRIO)", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", padx=16, pady=(14, 8))

            adv_card = ctk.CTkFrame(cols, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["red_border"])
            adv_card.grid(row=0, column=1, padx=(6, 0), sticky="nsew")
            ctk.CTkLabel(adv_card, text="LIMPEZA AVANÇADA (PRO DESBLOQUEADO)", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", padx=16, pady=(14, 8))

            self.cleanup_vars.clear()
            self.cleanup_size_labels.clear()

            for item in CLEANUP_ITEMS:
                parent_card = basic_card if item["col"] == "basic" else adv_card
                row = ctk.CTkFrame(parent_card, fg_color=COLORS["bg_surface"], corner_radius=8)
                row.pack(fill="x", padx=14, pady=4)

                var = ctk.BooleanVar(value=item["default_on"])
                self.cleanup_vars[item["id"]] = var

                chk = ctk.CTkCheckBox(
                    row,
                    text=item["name"],
                    variable=var,
                    font=FONTS["body_bold"],
                    text_color=COLORS["text_primary"],
                    fg_color=COLORS["red_primary"],
                    hover_color=COLORS["red_hover"],
                )
                chk.pack(side="top", anchor="w", padx=10, pady=(8, 2))

                bottom_row = ctk.CTkFrame(row, fg_color="transparent")
                bottom_row.pack(fill="x", padx=10, pady=(0, 8))
                ctk.CTkLabel(
                    bottom_row,
                    text=item["desc"],
                    font=FONTS["small"],
                    text_color=COLORS["text_secondary"],
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)

                sz_lbl = ctk.CTkLabel(
                    bottom_row,
                    text="Calculando...",
                    font=FONTS["mono"],
                    text_color=COLORS["ok"],
                )
                sz_lbl.pack(side="right", padx=(8, 0))
                self.cleanup_size_labels[item["id"]] = sz_lbl

            # Barra de ação de limpeza
            action_bar = ctk.CTkFrame(self.limpeza_content, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            action_bar.pack(fill="x", pady=6)

            self.total_cleanup_lbl = ctk.CTkLabel(
                action_bar,
                text="Analisando diretórios temporários...",
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
            )
            self.total_cleanup_lbl.pack(side="left", padx=18, pady=14)

            ctk.CTkButton(
                action_bar,
                text="🧹 Executar Limpeza Agora",
                fg_color=COLORS["red_primary"],
                hover_color=COLORS["red_hover"],
                font=FONTS["body_bold"],
                height=38,
                command=self._execute_selected_cleanup,
            ).pack(side="right", padx=18, pady=12)

            ctk.CTkButton(
                action_bar,
                text="🔄 Recalcular Espaço",
                fg_color=COLORS["bg_surface"],
                hover_color=COLORS["bg_card_hover"],
                font=FONTS["body"],
                height=38,
                command=self._measure_cleanup_bg,
            ).pack(side="right", padx=(0, 8), pady=12)

            self._measure_cleanup_bg()

        elif tab_id == "large":
            card = ctk.CTkFrame(self.limpeza_content, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            card.pack(fill="x")
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=18, pady=14)
            ctk.CTkLabel(
                top,
                text="Scanner de Arquivos Grandes (> 100 MB em Downloads, Desktop, Documentos e Vídeos)",
                font=FONTS["title_sm"],
                text_color=COLORS["text_primary"],
            ).pack(side="left")

            res_frame = ctk.CTkFrame(card, fg_color="transparent")
            res_frame.pack(fill="x", padx=18, pady=(0, 16))

            def _scan_large():
                for w in res_frame.winfo_children():
                    w.destroy()
                ctk.CTkLabel(res_frame, text="⏳ Escaneando pastas do usuário...", font=FONTS["body"]).pack(anchor="w")

                def _bg():
                    files = scan_large_files(min_size_mb=100)
                    self.after(0, lambda: _show_large(files))

                threading.Thread(target=_bg, daemon=True).start()

            def _show_large(files):
                for w in res_frame.winfo_children():
                    w.destroy()
                if not files:
                    ctk.CTkLabel(res_frame, text="✓ Nenhum arquivo acima de 100 MB encontrado nas pastas de usuário.", text_color=COLORS["ok"]).pack(anchor="w")
                    return
                for f in files[:25]:
                    r = ctk.CTkFrame(res_frame, fg_color=COLORS["bg_surface"], corner_radius=8)
                    r.pack(fill="x", pady=3)
                    ctk.CTkLabel(r, text=f["size_str"], font=FONTS["mono"], text_color=COLORS["red_bright"], width=95).pack(side="left", padx=10, pady=6)
                    ctk.CTkLabel(r, text=f["path"], font=FONTS["small"], text_color=COLORS["text_primary"], anchor="w").pack(side="left", fill="x", expand=True, padx=6)
                    ctk.CTkButton(
                        r,
                        text="Abrir Pasta",
                        width=90,
                        height=26,
                        fg_color=COLORS["bg_card"],
                        hover_color=COLORS["red_primary"],
                        font=FONTS["small"],
                        command=lambda p=f["path"]: subprocess.Popen(["explorer", "/select,", p]),
                    ).pack(side="right", padx=8, pady=4)

            ctk.CTkButton(
                top,
                text="🔍 Escanear Arquivos Grandes",
                fg_color=COLORS["red_primary"],
                hover_color=COLORS["red_hover"],
                command=_scan_large,
            ).pack(side="right")

        elif tab_id == "duplicates":
            card = ctk.CTkFrame(self.limpeza_content, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            card.pack(fill="x")
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=18, pady=14)
            ctk.CTkLabel(
                top,
                text="Scanner de Arquivos Duplicados por Hash SHA-256 (> 5 MB)",
                font=FONTS["title_sm"],
                text_color=COLORS["text_primary"],
            ).pack(side="left")

            res_frame = ctk.CTkFrame(card, fg_color="transparent")
            res_frame.pack(fill="x", padx=18, pady=(0, 16))

            def _scan_dups():
                for w in res_frame.winfo_children():
                    w.destroy()
                ctk.CTkLabel(res_frame, text="⏳ Comparando hashes SHA-256...", font=FONTS["body"]).pack(anchor="w")

                def _bg():
                    groups = scan_duplicate_files(min_size_mb=5)
                    self.after(0, lambda: _show_dups(groups))

                threading.Thread(target=_bg, daemon=True).start()

            def _show_dups(groups):
                for w in res_frame.winfo_children():
                    w.destroy()
                if not groups:
                    ctk.CTkLabel(res_frame, text="✓ Nenhum arquivo duplicado (> 5 MB) encontrado.", text_color=COLORS["ok"]).pack(anchor="w")
                    return
                for g in groups[:15]:
                    box = ctk.CTkFrame(res_frame, fg_color=COLORS["bg_surface"], corner_radius=8)
                    box.pack(fill="x", pady=4)
                    ctk.CTkLabel(
                        box,
                        text=f"Grupo Hash {g['hash']} · {g['count']} cópias ({g['size_each']} cada) · Desperdício: {g['wasted_str']}",
                        font=FONTS["body_bold"],
                        text_color=COLORS["red_bright"],
                        anchor="w",
                    ).pack(fill="x", padx=12, pady=(8, 4))
                    for fp in g["files"]:
                        ctk.CTkLabel(box, text=f"   • {fp}", font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", padx=12, pady=1)

            ctk.CTkButton(
                top,
                text="🔍 Buscar Duplicados",
                fg_color=COLORS["red_primary"],
                hover_color=COLORS["red_hover"],
                command=_scan_dups,
            ).pack(side="right")

    def _measure_cleanup_bg(self) -> None:
        def _worker():
            sizes = measure_cleanup_sizes()
            self.after(0, lambda: self._update_cleanup_sizes_ui(sizes))

        threading.Thread(target=_worker, daemon=True).start()

    def _update_cleanup_sizes_ui(self, sizes: Dict[str, int]) -> None:
        total = 0
        for cid, sz in sizes.items():
            total += sz
            lbl = self.cleanup_size_labels.get(cid)
            if lbl and lbl.winfo_exists():
                lbl.configure(text=format_bytes(sz) if cid != "recyclebin" else "Lixeira")
        if hasattr(self, "total_cleanup_lbl") and self.total_cleanup_lbl.winfo_exists():
            self.total_cleanup_lbl.configure(text=f"Espaço total estimado para liberação: {format_bytes(total)}")

    def _execute_selected_cleanup(self) -> None:
        selected = [cid for cid, var in self.cleanup_vars.items() if var.get()]
        if not selected:
            self.notify("⚠ Selecione pelo menos uma categoria para limpar.", "warn")
            return
        self.notify("⏳ Executando limpeza profunda...", "info")

        def _worker():
            res = run_cleanup(selected)
            self.after(0, lambda: self._on_cleanup_done(res))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_cleanup_done(self, res: Dict) -> None:
        self.notify(
            f"✓ Limpeza concluída! Espaço liberado: {res.get('freed_formatted')} ({res.get('removed_files')} arquivos/pastas removidos).",
            "ok",
        )
        self._measure_cleanup_bg()

    # =========================================================================
    # 4. PÁGINA: OTIMIZAÇÕES DO SISTEMA (5 SUB-ABAS)
    # =========================================================================
    def _build_otimizacoes_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="🚀",
            kicker="Ajustes de Baixo Nível do Windows",
            title="Otimizações do Sistema",
            subtitle="Visual & Latência, Serviços do Windows, Planos de Energia (Ultimate), Inicialização e Aplicativos.",
        ).pack(fill="x", pady=(0, 12))

        self.otim_content = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        SubTabBar(
            self.page_scroll,
            tabs=[
                ("visual", "🖥️ Visual & Sistema"),
                ("services", "⚙️ Serviços"),
                ("energy", "⚡ Plano de Energia"),
                ("startup", "🚀 Inicialização"),
                ("apps", "📦 Apps Instalados"),
            ],
            on_select=self._render_otim_subtab,
            initial="visual",
        ).pack(fill="x", pady=(0, 12))
        self.otim_content.pack(fill="both", expand=True)
        self._render_otim_subtab("visual")

    def _render_otim_subtab(self, tab_id: str) -> None:
        for w in self.otim_content.winfo_children():
            w.destroy()

        if tab_id == "visual":
            for tweak in VISUAL_TWEAKS:
                is_on = check_visual_tweak_state(tweak)
                row = ctk.CTkFrame(self.otim_content, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
                row.pack(fill="x", pady=4)

                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=16, pady=12)
                ctk.CTkLabel(info, text=tweak["name"], font=FONTS["title_sm"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
                ctk.CTkLabel(info, text=tweak["desc"], font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(2, 0))

                status_txt = "✓ APLICADO" if is_on else "PADRÃO"
                status_col = COLORS["ok"] if is_on else COLORS["text_muted"]
                ctk.CTkLabel(row, text=status_txt, font=("Segoe UI", 10, "bold"), text_color=status_col).pack(side="left", padx=10)

                ctk.CTkButton(
                    row,
                    text="Reverter" if is_on else "Aplicar",
                    width=100,
                    height=32,
                    fg_color=COLORS["bg_surface"] if is_on else COLORS["red_primary"],
                    hover_color=COLORS["red_hover"],
                    command=lambda tid=tweak["id"], state=not is_on: self._toggle_visual_tweak(tid, state),
                ).pack(side="right", padx=16, pady=12)

        elif tab_id == "services":
            services = get_services_status()
            for svc in services:
                running = svc["status"] == "Running"
                row = ctk.CTkFrame(self.otim_content, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
                row.pack(fill="x", pady=4)

                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=16, pady=10)
                ctk.CTkLabel(info, text=f"{svc['display']} ({svc['name']})", font=FONTS["title_sm"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
                ctk.CTkLabel(info, text=f"{svc['desc']}  ·  Risco: {svc['risk']}", font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")

                badge_col = COLORS["warn"] if running else COLORS["ok"]
                ctk.CTkLabel(row, text="EM EXECUÇÃO" if running else "PARADO / OTIMIZADO", font=("Segoe UI", 10, "bold"), text_color=badge_col).pack(side="left", padx=12)

                ctk.CTkButton(
                    row,
                    text="Desativar" if running else "Reativar",
                    width=105,
                    height=32,
                    fg_color=COLORS["red_primary"] if running else COLORS["bg_surface"],
                    hover_color=COLORS["red_hover"],
                    command=lambda sname=svc["name"], dis=running: self._handle_service_toggle(sname, dis),
                ).pack(side="right", padx=16, pady=10)

        elif tab_id == "energy":
            active_plan = get_active_power_plan()
            grid = ctk.CTkFrame(self.otim_content, fg_color="transparent")
            grid.pack(fill="x", pady=6)
            for i in range(4):
                grid.grid_columnconfigure(i, weight=1)

            for idx, plan in enumerate(POWER_PLANS):
                is_active = plan["id"] == active_plan
                card = ctk.CTkFrame(
                    grid,
                    fg_color=COLORS["bg_card_alt"] if plan["id"] == "ultimate" else COLORS["bg_card"],
                    corner_radius=12,
                    border_width=2 if is_active else 1,
                    border_color=COLORS["red_primary"] if is_active else COLORS["border"],
                )
                card.grid(row=0, column=idx, padx=6, sticky="nsew")

                ctk.CTkLabel(card, text=plan["badge"], font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", padx=16, pady=(14, 4))
                ctk.CTkLabel(card, text=plan["name"], font=FONTS["title_sm"], text_color=COLORS["text_primary"], wraplength=210, justify="left", anchor="w").pack(fill="x", padx=16, pady=(0, 6))
                ctk.CTkLabel(card, text=plan["desc"], font=FONTS["small"], text_color=COLORS["text_secondary"], wraplength=210, justify="left", anchor="w").pack(fill="x", padx=16, pady=(0, 14))

                ctk.CTkButton(
                    card,
                    text="✓ Plano Ativo" if is_active else "Ativar Plano",
                    state="disabled" if is_active else "normal",
                    fg_color=COLORS["ok_bg"] if is_active else COLORS["red_primary"],
                    hover_color=COLORS["red_hover"],
                    command=lambda pid=plan["id"]: self._handle_power_plan(pid),
                ).pack(fill="x", padx=16, pady=(0, 16))

        elif tab_id == "startup":
            items = list_startup_items()
            if not items:
                ctk.CTkLabel(self.otim_content, text="Nenhum programa extra encontrado nas chaves Run de inicialização.", font=FONTS["body"]).pack(pady=20)
            for it in items:
                row = ctk.CTkFrame(self.otim_content, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
                row.pack(fill="x", pady=4)
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=16, pady=10)
                ctk.CTkLabel(info, text=f"{it['name']}  ({it['source']}) · Impacto: {it['impact']}", font=FONTS["title_sm"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
                ctk.CTkLabel(info, text=it["path"], font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
                ctk.CTkButton(
                    row,
                    text="Remover do Boot",
                    width=130,
                    height=32,
                    fg_color=COLORS["red_primary"],
                    hover_color=COLORS["red_hover"],
                    command=lambda n=it["name"], h=it["hive"]: self._handle_remove_startup(n, h),
                ).pack(side="right", padx=16, pady=10)

        elif tab_id == "apps":
            apps = list_installed_apps(max_count=60)
            for app in apps:
                row = ctk.CTkFrame(self.otim_content, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(row, text=app["name"], font=FONTS["body_bold"], text_color=COLORS["text_primary"], anchor="w").pack(side="left", padx=14, pady=8)
                ctk.CTkLabel(row, text=f"{app['publisher']} · v{app['version']}", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(side="left", padx=10)
                if app["uninstall"]:
                    ctk.CTkButton(
                        row,
                        text="Desinstalar",
                        width=95,
                        height=28,
                        fg_color=COLORS["bg_surface"],
                        hover_color=COLORS["red_primary"],
                        font=FONTS["small"],
                        command=lambda cmd=app["uninstall"]: subprocess.Popen(cmd, shell=True),
                    ).pack(side="right", padx=12, pady=6)

    def _toggle_visual_tweak(self, tweak_id: str, enable: bool) -> None:
        res = apply_visual_tweak(tweak_id, enable)
        if res.get("success"):
            self.notify(f"✓ Ajuste '{tweak_id}' atualizado com sucesso!", "ok")
        else:
            self.notify(f"⚠ Falha ao aplicar '{tweak_id}': {res.get('error')} (Execute como Administrador)", "warn")
        self._render_otim_subtab("visual")

    def _handle_service_toggle(self, service_name: str, disable: bool) -> None:
        res = toggle_service(service_name, disable)
        if res.get("success"):
            self.notify(f"✓ Serviço {service_name} {'desativado' if disable else 'reativado'}.", "ok")
        else:
            self.notify(f"⚠ Não foi possível alterar {service_name} (Requer Administrador).", "warn")
        self._render_otim_subtab("services")

    def _handle_power_plan(self, plan_id: str) -> None:
        res = activate_power_plan(plan_id)
        if res.get("success"):
            self.notify(f"✓ Plano de energia '{plan_id.upper()}' ativado!", "ok")
        else:
            self.notify(f"⚠ Erro ao ativar plano: {res.get('error')}", "warn")
        self._render_otim_subtab("energy")

    def _handle_remove_startup(self, name: str, hive: str) -> None:
        res = remove_startup_item(name, hive)
        if res.get("success"):
            self.notify(f"✓ '{name}' removido da inicialização.", "ok")
        else:
            self.notify(f"⚠ Falha ao remover '{name}': {res.get('error')}", "warn")
        self._render_otim_subtab("startup")

    # =========================================================================
    # 5. PÁGINA: JOGOS & GAME BOOST
    # =========================================================================
    def _build_jogos_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="🎮",
            kicker="Performance Competitiva & Estabilidade de Frame Time",
            title="Jogos & Game Session Boost",
            subtitle="Ative HAGS, Prioridade MMCSS, Game Boost em 1 clique e visualize suas bibliotecas detectadas.",
        ).pack(fill="x", pady=(0, 12))

        # Card de Sessão Game Boost
        boost_card = ctk.CTkFrame(
            self.page_scroll,
            fg_color=COLORS["bg_card_alt"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["red_primary"],
        )
        boost_card.pack(fill="x", pady=(0, 14))
        top_b = ctk.CTkFrame(boost_card, fg_color="transparent")
        top_b.pack(fill="x", padx=18, pady=14)

        left_b = ctk.CTkFrame(top_b, fg_color="transparent")
        left_b.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(left_b, text="🔥 SESSÃO GAME BOOST INSTANTÂNEO", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x")
        ctk.CTkLabel(left_b, text="Suspende apps pesados em segundo plano e limpa a Memória RAM antes da partida", font=FONTS["title_md"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x", pady=(2, 4))
        ctk.CTkLabel(left_b, text="Encerra processos ociosos (OneDrive, Widgets, GameBar, Cortana) e executa EmptyWorkingSet em todos os processos.", font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")

        ctk.CTkButton(
            top_b,
            text="🚀 Ativar Game Boost Agora",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            font=FONTS["body_bold"],
            height=40,
            width=210,
            command=self._run_game_boost_ui,
        ).pack(side="right", padx=(12, 0))

        # Ajustes de Registro Gaming
        head_row = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        head_row.pack(fill="x", pady=(4, 6))
        ctk.CTkLabel(head_row, text="OTIMIZAÇÕES DE KERNEL, GPU E LATÊNCIA PARA JOGOS", font=FONTS["kicker"], text_color=COLORS["text_secondary"]).pack(side="left")
        ctk.CTkButton(
            head_row,
            text="⚡ Aplicar Todos os Ajustes Gaming",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            height=30,
            command=self._apply_all_gaming_ui,
        ).pack(side="right")

        for gt in GAMING_TWEAKS:
            is_on = check_gaming_tweak(gt)
            row = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=16, pady=12)
            ctk.CTkLabel(info, text=gt["kicker"], font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=gt["name"], font=FONTS["title_sm"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=gt["desc"], font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")

            ctk.CTkButton(
                row,
                text="✓ Ativo (Reverter)" if is_on else "Ativar Ajuste",
                width=145,
                height=34,
                fg_color=COLORS["ok_bg"] if is_on else COLORS["red_primary"],
                hover_color=COLORS["red_hover"],
                command=lambda gid=gt["id"], st=not is_on: self._toggle_gaming_ui(gid, st),
            ).pack(side="right", padx=16, pady=12)

        # Bibliotecas de Jogos Detectadas
        ctk.CTkLabel(
            self.page_scroll,
            text="BIBLIOTECAS E LAUNCHERS DETECTADOS NESTE PC",
            font=FONTS["kicker"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", pady=(14, 6))

        libs = detect_game_libraries()
        lib_grid = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        lib_grid.pack(fill="x")
        for idx, lib in enumerate(libs):
            lib_grid.grid_columnconfigure(idx, weight=1)
            lcard = ctk.CTkFrame(
                lib_grid,
                fg_color=COLORS["bg_card"],
                corner_radius=10,
                border_width=1,
                border_color=COLORS["red_border"] if lib["installed"] else COLORS["border"],
            )
            lcard.grid(row=0, column=idx, padx=4, sticky="nsew")
            ctk.CTkLabel(lcard, text=lib["name"], font=FONTS["title_sm"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x", padx=12, pady=(12, 2))
            st_txt = f"● Detectado ({lib['games_count']} jogos)" if lib["installed"] else "○ Não instalado"
            st_col = COLORS["ok"] if lib["installed"] else COLORS["text_muted"]
            ctk.CTkLabel(lcard, text=st_txt, font=FONTS["small"], text_color=st_col, anchor="w").pack(fill="x", padx=12, pady=(0, 12))

    def _run_game_boost_ui(self) -> None:
        res = run_game_session_boost()
        self.notify(
            f"🔥 Game Boost Ativado! {len(res.get('closed_apps', []))} processos fechados e +{res.get('freed_mb', 0)} MB de RAM liberados.",
            "ok",
        )

    def _toggle_gaming_ui(self, gid: str, enable: bool) -> None:
        res = apply_gaming_tweak(gid, enable)
        if res.get("success"):
            self.notify(f"✓ Ajuste gaming '{gid}' atualizado!", "ok")
        else:
            self.notify(f"⚠ Falha ao alterar '{gid}' (Requer Administrador).", "warn")
        self.show_page("jogos")

    def _apply_all_gaming_ui(self) -> None:
        res = apply_all_gaming_tweaks()
        self.notify(f"✓ {res.get('applied')}/{res.get('total')} otimizações de jogos aplicadas!", "ok")
        self.show_page("jogos")

    # =========================================================================
    # 6. PÁGINA: REDE & PING GAMER
    # =========================================================================
    def _build_rede_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="🌐",
            kicker="Redução de Latência, Jitter & Packet Loss",
            title="Otimização de Rede & DNS Benchmark",
            subtitle="Teste a estabilidade da conexão, descubra o DNS mais rápido para sua região e otimize a pilha TCP/IP.",
        ).pack(fill="x", pady=(0, 12))

        net_info = get_network_overview()
        conn_bar = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border_red"])
        conn_bar.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            conn_bar,
            text=f"● Status: {net_info['status']}   |   IPv4 Local: {net_info['ipv4']}   |   Ping Cloudflare (1.1.1.1): {net_info['ping_ms']} ms",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=18, pady=12)

        ctk.CTkButton(
            conn_bar,
            text="🔄 Resetar Rede (Flush DNS + Winsock)",
            fg_color=COLORS["red_dark"],
            hover_color=COLORS["red_primary"],
            border_width=1,
            border_color=COLORS["red_primary"],
            height=32,
            command=self._handle_winsock_reset,
        ).pack(side="right", padx=16, pady=10)

        # Grid de Testes (Benchmark DNS + Estabilidade/Jitter)
        test_grid = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        test_grid.pack(fill="x", pady=(0, 14))
        test_grid.grid_columnconfigure(0, weight=1)
        test_grid.grid_columnconfigure(1, weight=1)

        # Card Benchmark DNS
        dns_card = ctk.CTkFrame(test_grid, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        dns_card.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        ctk.CTkLabel(dns_card, text="BENCHMARK DE SERVIDORES DNS", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", padx=16, pady=(14, 4))
        self.dns_res_frame = ctk.CTkFrame(dns_card, fg_color="transparent")
        self.dns_res_frame.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(self.dns_res_frame, text="Clique abaixo para medir a latência dos servidores DNS.", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        ctk.CTkButton(
            dns_card,
            text="⚡ Testar Velocidade DNS",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            command=self._run_dns_bench_ui,
        ).pack(fill="x", padx=16, pady=(6, 14))

        # Card Teste de Estabilidade (Jitter & Perda)
        stab_card = ctk.CTkFrame(test_grid, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        stab_card.grid(row=0, column=1, padx=(6, 0), sticky="nsew")
        ctk.CTkLabel(stab_card, text="TESTE DE ESTABILIDADE (PING, JITTER & PERDA)", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", padx=16, pady=(14, 4))
        self.stab_res_frame = ctk.CTkFrame(stab_card, fg_color="transparent")
        self.stab_res_frame.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(self.stab_res_frame, text="Analisa oscilação (jitter) e perda de pacotes em tempo real.", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        ctk.CTkButton(
            stab_card,
            text="📡 Medir Estabilidade e Jitter",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            command=self._run_stability_ui,
        ).pack(fill="x", padx=16, pady=(6, 14))

        # Lista de Otimizações de Rede
        ctk.CTkLabel(
            self.page_scroll,
            text="AJUSTES DE LATÊNCIA E PRIORIDADE DE PACOTES (REVERSÍVEIS)",
            font=FONTS["kicker"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", pady=(4, 6))

        state_tweaks = logger.get_applied_state().get("tweaks", {})
        for nt in NETWORK_TWEAKS:
            applied = bool(state_tweaks.get(f"net.{nt['key']}", False))
            row = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=16, pady=12)
            ctk.CTkLabel(info, text=nt["name"], font=FONTS["title_sm"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=nt["desc"], font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")

            ctk.CTkButton(
                row,
                text="Desfazer" if applied else "Aplicar Ajuste",
                width=130,
                height=34,
                fg_color=COLORS["bg_surface"] if applied else COLORS["red_primary"],
                hover_color=COLORS["red_hover"],
                command=lambda k=nt["key"], en=not applied: self._toggle_net_tweak(k, en),
            ).pack(side="right", padx=16, pady=12)

    def _run_dns_bench_ui(self) -> None:
        for w in self.dns_res_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.dns_res_frame, text="⏳ Testando servidores DNS...", font=FONTS["small"]).pack(anchor="w")

        def _bg():
            rows = run_dns_benchmark()
            self.after(0, lambda: self._show_dns_bench(rows))

        threading.Thread(target=_bg, daemon=True).start()

    def _show_dns_bench(self, rows) -> None:
        if not hasattr(self, "dns_res_frame") or not self.dns_res_frame.winfo_exists():
            return
        for w in self.dns_res_frame.winfo_children():
            w.destroy()
        for idx, r in enumerate(rows):
            col = COLORS["ok"] if idx == 0 and r["ping_ms"] > 0 else COLORS["text_primary"]
            prefix = "🏆 " if idx == 0 else "   "
            ctk.CTkLabel(
                self.dns_res_frame,
                text=f"{prefix}{r['name']} ({r['ip']}) — {r['ping_ms']} ms",
                font=FONTS["mono"],
                text_color=col,
                anchor="w",
            ).pack(fill="x", pady=1)

    def _run_stability_ui(self) -> None:
        for w in self.stab_res_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.stab_res_frame, text="⏳ Disparando pacotes de teste...", font=FONTS["small"]).pack(anchor="w")

        def _bg():
            data = run_stability_test()
            self.after(0, lambda: self._show_stability(data))

        threading.Thread(target=_bg, daemon=True).start()

    def _show_stability(self, d: Dict) -> None:
        if not hasattr(self, "stab_res_frame") or not self.stab_res_frame.winfo_exists():
            return
        for w in self.stab_res_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.stab_res_frame,
            text=(
                f"Pacotes: {d['received']}/{d['sent']} recebidos (Perda: {d['loss_pct']}%)\n"
                f"Latência Mín/Méd/Máx: {d['min_ms']} ms / {d['avg_ms']} ms / {d['max_ms']} ms\n"
                f"Jitter Médio: {d['jitter_ms']} ms"
            ),
            font=FONTS["mono"],
            text_color=COLORS["ok"] if d["loss_pct"] == 0 else COLORS["warn"],
            justify="left",
            anchor="w",
        ).pack(fill="x")

    def _toggle_net_tweak(self, key: str, enable: bool) -> None:
        res = apply_network_tweak(key, enable)
        if res.get("success"):
            self.notify(f"✓ Ajuste de rede '{key}' {'aplicado' if enable else 'revertido'}!", "ok")
        else:
            self.notify(f"⚠ Erro ao aplicar '{key}': {res.get('error')}", "warn")
        self.show_page("rede")

    def _handle_winsock_reset(self) -> None:
        res = reset_network_stack()
        self.notify(
            f"✓ Pilha de rede resetada ({res.get('ok_steps')}/{res.get('total_steps')} comandos concluídos). Reinicie o PC se necessário.",
            "ok",
        )

    # =========================================================================
    # 7. PÁGINA: PRIVACIDADE & TELEMETRIA
    # =========================================================================
    def _build_privacidade_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="🛡️",
            kicker="Blindagem de Dados & Bloqueio de Telemetria",
            title="Privacidade & Anti-Telemetria",
            subtitle="Desative rastreamento publicitário, coleta de diagnóstico da Microsoft, busca Bing no Menu Iniciar e bloatwares.",
        ).pack(fill="x", pady=(0, 12))

        batch_card = ctk.CTkFrame(
            self.page_scroll,
            fg_color=COLORS["bg_card_alt"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["red_primary"],
        )
        batch_card.pack(fill="x", pady=(0, 14))
        b_row = ctk.CTkFrame(batch_card, fg_color="transparent")
        b_row.pack(fill="x", padx=18, pady=14)
        ctk.CTkLabel(
            b_row,
            text="🛡️ Blindagem Completa em 1 Clique — Aplica todas as 8 regras de privacidade simultaneamente",
            font=FONTS["title_sm"],
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            b_row,
            text="Reverter Todos",
            fg_color=COLORS["bg_surface"],
            hover_color=COLORS["bg_card_hover"],
            width=120,
            command=lambda: self._apply_privacy_batch(False),
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            b_row,
            text="⚡ Blindar Privacidade Agora",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            font=FONTS["body_bold"],
            command=lambda: self._apply_privacy_batch(True),
        ).pack(side="right")

        for item in PRIVACY_ITEMS:
            is_on = check_privacy_item(item)
            row = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=16, pady=12)
            ctk.CTkLabel(info, text=f"{item['name']}  ·  [{item['risk']}]", font=FONTS["title_sm"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=item["desc"], font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")

            ctk.CTkButton(
                row,
                text="✓ Protegido (Reverter)" if is_on else "Bloquear Coleta",
                width=155,
                height=34,
                fg_color=COLORS["ok_bg"] if is_on else COLORS["red_primary"],
                hover_color=COLORS["red_hover"],
                command=lambda pid=item["id"], st=not is_on: self._toggle_privacy_single(pid, st),
            ).pack(side="right", padx=16, pady=12)

    def _toggle_privacy_single(self, item_id: str, enable: bool) -> None:
        res = apply_privacy_item(item_id, enable)
        if res.get("success"):
            self.notify(f"✓ Regra de privacidade '{item_id}' atualizada!", "ok")
        else:
            self.notify(f"⚠ Falha ao alterar '{item_id}' (Execute como Administrador).", "warn")
        self.show_page("privacidade")

    def _apply_privacy_batch(self, enable: bool) -> None:
        res = apply_all_privacy(enable)
        self.notify(
            f"✓ {res.get('applied')}/{res.get('total')} regras de privacidade {'aplicadas' if enable else 'revertidas'}!",
            "ok",
        )
        self.show_page("privacidade")

    # =========================================================================
    # 8. PÁGINA: ATUALIZAÇÕES (WINGET) & WINSAT SCORE
    # =========================================================================
    def _build_atualizacoes_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="🔄",
            kicker="Gerenciador de Pacotes Winget & Índice de Experiência do Windows",
            title="Atualizações de Programas & WinSAT",
            subtitle="Verifique programas desatualizados via Winget oficial e consulte a nota de hardware do seu PC.",
        ).pack(fill="x", pady=(0, 12))

        # Card WinSAT Score
        winsat = get_winsat_scores()
        ws_card = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border_red"])
        ws_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(ws_card, text="ÍNDICE DE EXPERIÊNCIA DO WINDOWS (WINSAT SCORE · ESCALA 1.0 A 9.9)", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", padx=18, pady=(14, 6))

        scores_row = ctk.CTkFrame(ws_card, fg_color="transparent")
        scores_row.pack(fill="x", padx=18, pady=(0, 14))
        items_ws = [
            ("Nota Base", winsat["base"]),
            ("Processador (CPU)", winsat["cpu"]),
            ("Memória RAM", winsat["memory"]),
            ("Gráficos Desktop", winsat["graphics"]),
            ("Gráficos 3D/Jogos", winsat["gaming"]),
            ("Disco Primário", winsat["disk"]),
        ]
        for idx, (label, val) in enumerate(items_ws):
            scores_row.grid_columnconfigure(idx, weight=1)
            b = ctk.CTkFrame(scores_row, fg_color=COLORS["bg_surface"], corner_radius=8)
            b.grid(row=0, column=idx, padx=4, sticky="nsew")
            ctk.CTkLabel(b, text=label, font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(pady=(8, 2))
            ctk.CTkLabel(
                b,
                text=f"{val:.1f}" if winsat["evaluated"] else "N/A",
                font=FONTS["mono_lg"],
                text_color=COLORS["red_bright"] if idx == 0 else COLORS["text_primary"],
            ).pack(pady=(0, 8))

        # Card Winget Updates
        wg_card = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        wg_card.pack(fill="x")
        top_wg = ctk.CTkFrame(wg_card, fg_color="transparent")
        top_wg.pack(fill="x", padx=18, pady=14)
        ctk.CTkLabel(top_wg, text="ATUALIZADOR DE PROGRAMAS (WINGET)", font=FONTS["title_sm"], text_color=COLORS["text_primary"]).pack(side="left")

        self.wg_list_frame = ctk.CTkFrame(wg_card, fg_color="transparent")
        self.wg_list_frame.pack(fill="x", padx=18, pady=(0, 16))
        ctk.CTkLabel(self.wg_list_frame, text="Clique em 'Buscar Atualizações' para escanear seus aplicativos instalados.", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(anchor="w")

        ctk.CTkButton(
            top_wg,
            text="⚡ Atualizar Todos Silenciosamente",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            command=self._upgrade_all_winget_ui,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            top_wg,
            text="🔍 Buscar Atualizações",
            fg_color=COLORS["bg_surface"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["red_border"],
            command=self._scan_winget_ui,
        ).pack(side="right")

    def _scan_winget_ui(self) -> None:
        for w in self.wg_list_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.wg_list_frame, text="⏳ Consultando repositório Winget...", font=FONTS["body"]).pack(anchor="w")

        def _bg():
            apps = check_winget_updates()
            self.after(0, lambda: self._show_winget_list(apps))

        threading.Thread(target=_bg, daemon=True).start()

    def _show_winget_list(self, apps) -> None:
        if not hasattr(self, "wg_list_frame") or not self.wg_list_frame.winfo_exists():
            return
        for w in self.wg_list_frame.winfo_children():
            w.destroy()
        if not apps:
            ctk.CTkLabel(self.wg_list_frame, text="✓ Todos os programas compatíveis estão atualizados (ou nenhum pacote pendente).", text_color=COLORS["ok"]).pack(anchor="w")
            return
        for a in apps:
            r = ctk.CTkFrame(self.wg_list_frame, fg_color=COLORS["bg_surface"], corner_radius=8)
            r.pack(fill="x", pady=3)
            ctk.CTkLabel(r, text=a["name"], font=FONTS["body_bold"], text_color=COLORS["text_primary"], anchor="w").pack(side="left", padx=12, pady=6)
            ctk.CTkLabel(r, text=f"{a['current']}  →  {a['available']}", font=FONTS["mono"], text_color=COLORS["red_bright"]).pack(side="right", padx=12)

    def _upgrade_all_winget_ui(self) -> None:
        self.notify("⏳ Atualizando programas em segundo plano via Winget...", "info")

        def _bg():
            res = upgrade_all_winget()
            self.after(
                0,
                lambda: self.notify(
                    "✓ Comando Winget Upgrade All concluído!" if res.get("success") else "⚠ Winget finalizou com avisos.",
                    "ok",
                ),
            )

        threading.Thread(target=_bg, daemon=True).start()

    # =========================================================================
    # 9. PÁGINA: AGENDADOR AUTOMÁTICO
    # =========================================================================
    def _build_agendar_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="⏰",
            kicker="Manutenção Automática Inteligente",
            title="Agendador de Tarefas Neitan",
            subtitle="Programe limpezas ou aplicação de perfis sem limites de agendamentos.",
        ).pack(fill="x", pady=(0, 12))

        form_card = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["red_border"])
        form_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(form_card, text="CRIAR NOVO AGENDAMENTO AUTOMÁTICO", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", padx=18, pady=(14, 8))

        controls = ctk.CTkFrame(form_card, fg_color="transparent")
        controls.pack(fill="x", padx=18, pady=(0, 14))

        self.sched_job_var = ctk.StringVar(value="Limpeza Completa")
        ctk.CTkOptionMenu(
            controls,
            values=["Limpeza Completa", "Perfil Gamer Competitivo", "Boost de Memória RAM", "Diagnóstico de Rede"],
            variable=self.sched_job_var,
            fg_color=COLORS["bg_surface"],
            button_color=COLORS["red_primary"],
            width=220,
        ).pack(side="left", padx=(0, 10))

        self.sched_rec_var = ctk.StringVar(value="Semanal")
        ctk.CTkOptionMenu(
            controls,
            values=["Diário", "Semanal", "Mensal", "A cada 6 horas"],
            variable=self.sched_rec_var,
            fg_color=COLORS["bg_surface"],
            button_color=COLORS["red_primary"],
            width=150,
        ).pack(side="left", padx=(0, 10))

        self.sched_time_entry = ctk.CTkEntry(
            controls,
            placeholder_text="03:00",
            width=90,
            fg_color=COLORS["bg_surface"],
        )
        self.sched_time_entry.insert(0, "03:00")
        self.sched_time_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            controls,
            text="＋ Salvar Agendamento",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            font=FONTS["body_bold"],
            command=self._save_schedule_ui,
        ).pack(side="right")

        schedules = get_schedules()
        if not schedules:
            ctk.CTkLabel(self.page_scroll, text="Nenhuma tarefa agendada ainda. Crie uma acima!", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(pady=16)
        for s in schedules:
            row = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(
                row,
                text=f"⏰ {s['job_type']}  ·  Recorrência: {s['recurrence']} às {s['time']}  ·  Criado em {s['created_at']}",
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=16, pady=12)
            ctk.CTkButton(
                row,
                text="Remover",
                width=90,
                height=30,
                fg_color=COLORS["bad_bg"],
                hover_color=COLORS["bad"],
                command=lambda sid=s["id"]: self._delete_schedule_ui(sid),
            ).pack(side="right", padx=16, pady=10)

    def _save_schedule_ui(self) -> None:
        t_val = self.sched_time_entry.get().strip() or "03:00"
        save_schedule(self.sched_job_var.get(), self.sched_rec_var.get(), t_val)
        self.notify("✓ Tarefa agendada salva com sucesso!", "ok")
        self.show_page("agendar")

    def _delete_schedule_ui(self, sched_id: str) -> None:
        delete_schedule(sched_id)
        self.notify("✓ Agendamento removido.", "info")
        self.show_page("agendar")

    # =========================================================================
    # 10. PÁGINA: HISTÓRICO, PONTOS DE RESTAURAÇÃO & LOGS
    # =========================================================================
    def _build_historico_page(self) -> None:
        PageHeader(
            self.page_scroll,
            icon_text="📜",
            kicker="Segurança, Reversão & Auditoria Completa",
            title="Histórico, Pontos de Restauração & Logs",
            subtitle="Crie um Ponto de Restauração do Windows, reverta sessões aplicadas ou inspecione os logs.",
        ).pack(fill="x", pady=(0, 12))

        # Barra de Ponto de Restauração
        rp_card = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card_alt"], corner_radius=12, border_width=1, border_color=COLORS["red_primary"])
        rp_card.pack(fill="x", pady=(0, 14))
        rp_row = ctk.CTkFrame(rp_card, fg_color="transparent")
        rp_row.pack(fill="x", padx=18, pady=14)
        ctk.CTkLabel(
            rp_row,
            text="🛡️ Rede de Segurança: Ativa a Proteção do Disco C:, remove limite de 24h e cria Ponto Oficial do Windows",
            font=FONTS["title_sm"],
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            rp_row,
            text="📂 Abrir Restauração (rstrui)",
            fg_color=COLORS["bg_surface"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["red_border"],
            font=FONTS["body_bold"],
            command=open_windows_restore_ui,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            rp_row,
            text="🛡️ Criar Ponto de Restauração Agora",
            fg_color=COLORS["red_primary"],
            hover_color=COLORS["red_hover"],
            font=FONTS["body_bold"],
            command=self._create_rp_ui,
        ).pack(side="right")

        # Lista de Pontos de Restauração do Windows detectados
        points = list_restore_points()
        if points:
            ctk.CTkLabel(
                self.page_scroll,
                text="PONTOS DE RESTAURAÇÃO DO WINDOWS SALVOS NO DISCO (SYSTEM VOLUME INFORMATION)",
                font=FONTS["kicker"],
                text_color=COLORS["red_bright"],
                anchor="w",
            ).pack(fill="x", pady=(0, 6))
            for pt in points[:8]:
                prow = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
                prow.pack(fill="x", pady=2)
                ctk.CTkLabel(
                    prow,
                    text=f"🛡️ #{pt['id']} — {pt['description']}   (Criado em: {pt['created_at']})",
                    font=FONTS["body_bold"],
                    text_color=COLORS["ok"],
                ).pack(side="left", padx=14, pady=8)

        # Sessões Aplicadas (Reversíveis)
        ctk.CTkLabel(self.page_scroll, text="SESSÕES DE PERFIS APLICADOS (REVERSÃO EM 1 CLIQUE)", font=FONTS["kicker"], text_color=COLORS["red_bright"], anchor="w").pack(fill="x", pady=(4, 6))
        sessions = logger.get_sessions()
        if not sessions:
            ctk.CTkLabel(self.page_scroll, text="Nenhuma sessão de perfil aplicada ainda.", font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(0, 10))
        for sess in sessions[:10]:
            srow = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            srow.pack(fill="x", pady=3)
            ctk.CTkLabel(
                srow,
                text=f"🎯 {sess['profileName']} ({sess['sessionId']}) · {sess['timestamp']} · {sess['itemCount']} ajustes aplicados",
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=16, pady=10)
            ctk.CTkButton(
                srow,
                text="↩ Reverter Sessão",
                width=130,
                height=30,
                fg_color=COLORS["warn_bg"],
                hover_color=COLORS["warn"],
                text_color=COLORS["text_primary"],
                command=lambda sid=sess["sessionId"]: self._revert_session_ui(sid),
            ).pack(side="right", padx=16, pady=8)

        # Registro de Auditoria (Action Logs)
        log_head = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        log_head.pack(fill="x", pady=(14, 6))
        ctk.CTkLabel(log_head, text="REGISTRO DE ATIVIDADES E AUDITORIA (LOGS)", font=FONTS["kicker"], text_color=COLORS["red_bright"]).pack(side="left")
        ctk.CTkButton(
            log_head,
            text="Abrir Pasta de Logs",
            height=28,
            fg_color=COLORS["bg_surface"],
            hover_color=COLORS["bg_card_hover"],
            command=lambda: os.startfile(str(logger.base_dir)),
        ).pack(side="right")

        logs = logger.get_logs()
        log_box = ctk.CTkFrame(self.page_scroll, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
        log_box.pack(fill="x", pady=(0, 14))
        if not logs:
            ctk.CTkLabel(log_box, text="Nenhuma ação registrada ainda.", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(padx=16, pady=14, anchor="w")
        for entry in logs[:25]:
            icon = "✓" if entry["success"] else "✗"
            col = COLORS["ok"] if entry["success"] else COLORS["bad"]
            line_txt = f"[{entry['timestamp']}]  {icon}  [{entry['module']}] {entry['action']}"
            if entry.get("details"):
                line_txt += f" — {entry['details']}"
            ctk.CTkLabel(log_box, text=line_txt, font=FONTS["mono"], text_color=col, anchor="w").pack(fill="x", padx=14, pady=2)

    def _create_rp_ui(self) -> None:
        self.notify("⏳ Ativando Proteção do Sistema e criando Ponto de Restauração no Windows...", "info")

        def _bg():
            res = create_restore_point("NeitanOtimizador - Ponto de Segurança")
            self.after(
                0,
                lambda: (
                    self.notify(
                        "✓ Ponto de Restauração criado com sucesso no Windows!" if res.get("success") else f"⚠ Não foi possível criar Ponto de Restauração: {res.get('error')}",
                        "ok" if res.get("success") else "warn",
                    ),
                    self.show_page("historico") if self.current_page == "historico" else None,
                ),
            )

        threading.Thread(target=_bg, daemon=True).start()

    def _revert_session_ui(self, session_id: str) -> None:
        res = revert_session(session_id)
        if res.get("success"):
            self.notify(f"✓ Sessão {session_id} revertida ({res.get('reverted_count')} ajustes restaurados).", "ok")
        else:
            self.notify(f"⚠ Erro ao reverter sessão: {res.get('error')}", "warn")
        self.show_page("historico")
