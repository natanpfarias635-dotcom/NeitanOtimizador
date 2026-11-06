# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Componentes Visuais CustomTkinter (Tema Vermelho & Preto)
"""

from typing import Callable, List, Tuple
import customtkinter as ctk

from src.theme import COLORS, FONTS


class PageHeader(ctk.CTkFrame):
    """Cabeçalho padrão das páginas no estilo OtimizePC, porém na paleta Vermelho & Preto."""

    def __init__(self, master, icon_text: str, kicker: str, title: str, subtitle: str, right_badge_text: str = "100% LIBERADO · PRO"):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)

        icon_box = ctk.CTkFrame(
            self,
            width=46,
            height=46,
            corner_radius=12,
            fg_color=COLORS["red_muted_bg"],
            border_width=1,
            border_color=COLORS["red_border"],
        )
        icon_box.grid(row=0, column=0, rowspan=2, padx=(0, 14), pady=2, sticky="n")
        icon_box.grid_propagate(False)
        ctk.CTkLabel(
            icon_box,
            text=icon_text,
            font=("Segoe UI Emoji", 20, "bold"),
            text_color=COLORS["red_bright"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            text_frame,
            text=kicker.upper(),
            font=FONTS["kicker"],
            text_color=COLORS["red_bright"],
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            text_frame,
            text=title,
            font=FONTS["title_lg"],
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(1, 2))

        ctk.CTkLabel(
            text_frame,
            text=subtitle,
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x")

        if right_badge_text:
            badge = ctk.CTkFrame(
                self,
                fg_color=COLORS["red_dark"],
                border_width=1,
                border_color=COLORS["red_primary"],
                corner_radius=999,
            )
            badge.grid(row=0, column=2, padx=(10, 0), sticky="ne")
            ctk.CTkLabel(
                badge,
                text=right_badge_text,
                font=("Segoe UI", 10, "bold"),
                text_color=COLORS["red_bright"],
            ).pack(padx=12, pady=4)


class SubTabBar(ctk.CTkFrame):
    """Barra de sub-abas horizontal com destaque em vermelho carmesim."""

    def __init__(self, master, tabs: List[Tuple[str, str]], on_select: Callable[[str], None], initial: str = ""):
        super().__init__(
            master,
            fg_color=COLORS["bg_surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.on_select = on_select
        self.buttons = {}
        self.active_id = initial or (tabs[0][0] if tabs else "")

        for idx, (tab_id, label) in enumerate(tabs):
            self.grid_columnconfigure(idx, weight=1)
            btn = ctk.CTkButton(
                self,
                text=label,
                height=34,
                corner_radius=8,
                font=FONTS["body_bold"],
                command=lambda tid=tab_id: self.select(tid),
            )
            btn.grid(row=0, column=idx, padx=4, pady=4, sticky="ew")
            self.buttons[tab_id] = btn

        self._refresh_styles()

    def select(self, tab_id: str) -> None:
        self.active_id = tab_id
        self._refresh_styles()
        self.on_select(tab_id)

    def _refresh_styles(self) -> None:
        for tid, btn in self.buttons.items():
            if tid == self.active_id:
                btn.configure(
                    fg_color=COLORS["red_primary"],
                    hover_color=COLORS["red_hover"],
                    text_color=COLORS["text_primary"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=COLORS["bg_card_hover"],
                    text_color=COLORS["text_secondary"],
                )


class MetricCard(ctk.CTkFrame):
    """Card de métrica ao vivo com barra de progresso em vermelho/preto."""

    def __init__(self, master, title: str, initial_value: str = "0%", subtitle: str = ""):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        ctk.CTkLabel(
            self,
            text=title.upper(),
            font=FONTS["kicker"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 2))

        self.val_label = ctk.CTkLabel(
            self,
            text=initial_value,
            font=FONTS["metric"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.val_label.pack(fill="x", padx=16, pady=(0, 6))

        self.progress = ctk.CTkProgressBar(
            self,
            height=7,
            corner_radius=99,
            fg_color=COLORS["bg_surface"],
            progress_color=COLORS["red_primary"],
        )
        self.progress.pack(fill="x", padx=16, pady=(0, 8))
        self.progress.set(0.0)

        self.sub_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self.sub_label.pack(fill="x", padx=16, pady=(0, 14))

    def update_metric(self, value_text: str, ratio: float, subtitle_text: str = "") -> None:
        self.val_label.configure(text=value_text)
        self.progress.set(max(0.0, min(1.0, ratio)))
        if subtitle_text:
            self.sub_label.configure(text=subtitle_text)
