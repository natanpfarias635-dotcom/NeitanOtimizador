# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Ponto de Entrada Principal
Verifica privilégios e inicializa a interface gráfica Vermelho & Preto.
"""

import ctypes
import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ui.app_window import NeitanOtimizadorApp


def main() -> None:
    try:
        # Habilita DPI Awareness no Windows 10/11 para nitidez máxima
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = NeitanOtimizadorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
