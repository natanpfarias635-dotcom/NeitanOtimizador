# -*- coding: utf-8 -*-
"""
Gera o ícone oficial do NeitanOtimizador (Vermelho & Preto) em alta resolução (.ico)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def generate_icon() -> Path:
    assets_dir = Path(__file__).resolve().parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    ico_path = assets_dir / "neitan_icon.ico"

    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo quadrado arredondado Preto Obsidiana com borda Vermelho Carmesim
    draw.rounded_rectangle(
        [(8, 8), (size - 8, size - 8)],
        radius=54,
        fill=(10, 10, 14, 255),
        outline=(225, 29, 72, 255),
        width=10,
    )

    # Detalhe interno em vermelho escuro
    draw.rounded_rectangle(
        [(26, 26), (size - 26, size - 26)],
        radius=40,
        fill=(24, 10, 16, 255),
        outline=(255, 42, 84, 180),
        width=3,
    )

    # Desenha um "N" estilizado geométrico em Vermelho Vibrante e Branco
    # Haste esquerda
    draw.polygon([(68, 196), (68, 60), (98, 60), (98, 196)], fill=(255, 42, 84, 255))
    # Haste direita
    draw.polygon([(158, 196), (158, 60), (188, 60), (188, 196)], fill=(255, 42, 84, 255))
    # Diagonal central
    draw.polygon([(68, 60), (98, 60), (188, 196), (158, 196)], fill=(248, 250, 252, 255))

    img.save(
        ico_path,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print(f"Icone criado em: {ico_path}")
    return ico_path


if __name__ == "__main__":
    generate_icon()
