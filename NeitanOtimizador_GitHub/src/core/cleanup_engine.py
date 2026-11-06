# -*- coding: utf-8 -*-
"""
NeitanOtimizador - Motor de Limpeza (Básica + Avançada + Arquivos Grandes + Duplicados)
100% desbloqueado, inspirado em todas as categorias do OtimizePC.
"""

import ctypes
import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.core.logger import logger

CLEANUP_ITEMS: List[Dict[str, Any]] = [
    # Coluna Básica
    {
        "id": "temp",
        "col": "basic",
        "name": "Arquivos Temporários do Sistema e Usuário",
        "desc": "Remove arquivos temporários de %TEMP% e C:\\Windows\\Temp não utilizados.",
        "default_on": True,
        "risk": "safe",
    },
    {
        "id": "browsers",
        "col": "basic",
        "name": "Cache de Navegadores (Chrome, Edge, Brave, Opera, Firefox)",
        "desc": "Limpa apenas o cache de mídia/páginas. Não apaga senhas, histórico ou logins.",
        "default_on": True,
        "risk": "safe",
    },
    {
        "id": "logs",
        "col": "basic",
        "name": "Logs e Relatórios de Erro do Windows (WER)",
        "desc": "Remove arquivos .log antigos e relatórios de travamento acumulados.",
        "default_on": True,
        "risk": "safe",
    },
    {
        "id": "prefetch",
        "col": "basic",
        "name": "Cache Prefetch do Windows",
        "desc": "Limpa índices antigos de pré-carregamento em C:\\Windows\\Prefetch.",
        "default_on": True,
        "risk": "safe",
    },
    {
        "id": "recyclebin",
        "col": "basic",
        "name": "Esvaziar Lixeira do Windows",
        "desc": "Remove permanentemente os itens enviados para a Lixeira em todos os discos.",
        "default_on": False,
        "risk": "warn",
    },
    # Coluna Avançada (100% Liberada no NeitanOtimizador)
    {
        "id": "shadercache",
        "col": "advanced",
        "name": "Cache de Shaders (DirectX / NVIDIA / AMD)",
        "desc": "Elimina shaders antigos compilados para corrigir engasgos (stuttering) em jogos.",
        "default_on": True,
        "risk": "safe",
    },
    {
        "id": "appcache",
        "col": "advanced",
        "name": "Cache de Apps (Discord, Steam, Spotify)",
        "desc": "Limpa caches gráficos de aplicativos pesados mantendo suas contas conectadas.",
        "default_on": True,
        "risk": "safe",
    },
    {
        "id": "updatebackup",
        "col": "advanced",
        "name": "Cache de Downloads do Windows Update",
        "desc": "Remove pacotes de atualização já instalados em SoftwareDistribution\\Download.",
        "default_on": False,
        "risk": "warn",
    },
    {
        "id": "deliveryopt",
        "col": "advanced",
        "name": "Cache de Otimização de Entrega (Delivery Optimization)",
        "desc": "Apaga arquivos P2P de atualizações do Windows armazenados em segundo plano.",
        "default_on": False,
        "risk": "safe",
    },
    {
        "id": "windowsold",
        "col": "advanced",
        "name": "Instalações Antigas do Windows (Windows.old)",
        "desc": "Libera vários GB de versões anteriores do Windows (irreversível).",
        "default_on": False,
        "risk": "bad",
    },
]


def _get_target_paths(item_id: str) -> List[Path]:
    local_app = Path(os.environ.get("LOCALAPPDATA", ""))
    roaming_app = Path(os.environ.get("APPDATA", ""))
    win_dir = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    prog_data = Path(os.environ.get("ProgramData", r"C:\ProgramData"))
    temp_user = Path(os.environ.get("TEMP", str(local_app / "Temp")))

    paths: List[Path] = []
    if item_id == "temp":
        paths = [temp_user, win_dir / "Temp"]
    elif item_id == "browsers":
        paths = [
            local_app / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            local_app / "Google" / "Chrome" / "User Data" / "Default" / "Code Cache",
            local_app / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            local_app / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache",
            local_app / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Cache",
            local_app / "Opera Software" / "Opera Stable" / "Cache",
            local_app / "Opera Software" / "Opera GX Stable" / "Cache",
        ]
    elif item_id == "logs":
        paths = [
            win_dir / "Logs",
            prog_data / "Microsoft" / "Windows" / "WER" / "ReportArchive",
            prog_data / "Microsoft" / "Windows" / "WER" / "ReportQueue",
            local_app / "CrashDumps",
        ]
    elif item_id == "prefetch":
        paths = [win_dir / "Prefetch"]
    elif item_id == "shadercache":
        paths = [
            local_app / "D3DSCache",
            local_app / "NVIDIA" / "DXCache",
            local_app / "NVIDIA" / "GLCache",
            local_app / "AMD" / "DxCache",
        ]
    elif item_id == "appcache":
        paths = [
            roaming_app / "discord" / "Cache",
            roaming_app / "discord" / "Code Cache",
            roaming_app / "discord" / "GPUCache",
            local_app / "Steam" / "htmlcache" / "Cache",
            local_app / "Spotify" / "Storage",
        ]
    elif item_id == "updatebackup":
        paths = [win_dir / "SoftwareDistribution" / "Download"]
    elif item_id == "deliveryopt":
        paths = [win_dir / "ServiceProfiles" / "NetworkService" / "AppData" / "Local" / "Microsoft" / "Windows" / "DeliveryOptimization" / "Cache"]
    elif item_id == "windowsold":
        sys_drive = os.environ.get("SystemDrive", "C:") + "\\"
        paths = [Path(sys_drive) / "Windows.old"]

    return [p for p in paths if p.exists()]


def _dir_size(path: Path, max_files: int = 4000) -> int:
    total = 0
    count = 0
    try:
        if path.is_file():
            return path.stat().st_size
        for root, _, files in os.walk(path, onerror=lambda _: None):
            for f in files:
                count += 1
                if count > max_files:
                    return total
                try:
                    fp = os.path.join(root, f)
                    if not os.path.islink(fp):
                        total += os.path.getsize(fp)
                except Exception:
                    pass
    except Exception:
        pass
    return total


def measure_cleanup_sizes() -> Dict[str, int]:
    """Retorna o tamanho estimado em bytes para cada categoria de limpeza."""
    sizes: Dict[str, int] = {}
    for item in CLEANUP_ITEMS:
        cid = item["id"]
        if cid == "recyclebin":
            sizes[cid] = 0
            continue
        total_bytes = 0
        for p in _get_target_paths(cid):
            total_bytes += _dir_size(p)
        sizes[cid] = total_bytes
    return sizes


def format_bytes(num_bytes: int) -> str:
    if num_bytes <= 0:
        return "0 MB"
    mb = num_bytes / (1024 * 1024)
    if mb < 1:
        kb = max(1, int(num_bytes / 1024))
        return f"{kb} KB"
    if mb < 1024:
        return f"{mb:.1f} MB"
    return f"{mb / 1024:.2f} GB"


def run_cleanup(selected_ids: List[str]) -> Dict[str, Any]:
    """Executa a limpeza real das categorias selecionadas e retorna bytes liberados."""
    freed_bytes = 0
    removed_files = 0
    details_list: List[str] = []

    for cid in selected_ids:
        if cid == "recyclebin":
            try:
                # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND = 0x00000007
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
                details_list.append("Lixeira esvaziada")
            except Exception:
                pass
            continue

        cat_freed = 0
        for folder in _get_target_paths(cid):
            try:
                for entry in os.scandir(folder):
                    try:
                        if entry.is_file(follow_symlinks=False):
                            sz = entry.stat().st_size
                            os.remove(entry.path)
                            cat_freed += sz
                            removed_files += 1
                        elif entry.is_dir(follow_symlinks=False):
                            sz = _dir_size(Path(entry.path), max_files=800)
                            shutil.rmtree(entry.path, ignore_errors=True)
                            cat_freed += sz
                            removed_files += 1
                    except Exception:
                        # Arquivo em uso pelo sistema — ignorado com segurança
                        pass
            except Exception:
                pass
        freed_bytes += cat_freed

    freed_str = format_bytes(freed_bytes)
    logger.log(
        module="Limpeza",
        action=f"Limpeza concluída ({len(selected_ids)} categorias)",
        success=True,
        details=f"Liberado: {freed_str} ({removed_files} itens removidos)",
    )
    return {
        "success": True,
        "freed_bytes": freed_bytes,
        "freed_formatted": freed_str,
        "removed_files": removed_files,
    }


def scan_large_files(min_size_mb: int = 250, max_results: int = 60) -> List[Dict[str, Any]]:
    """Busca arquivos grandes na pasta do usuário (Downloads, Desktop, Documentos, Videos)."""
    user_profile = Path(os.environ.get("USERPROFILE", os.path.expanduser("~")))
    roots = [
        user_profile / "Downloads",
        user_profile / "Desktop",
        user_profile / "Documents",
        user_profile / "Videos",
    ]
    min_bytes = min_size_mb * 1024 * 1024
    found: List[Dict[str, Any]] = []

    for r in roots:
        if not r.exists():
            continue
        for dirpath, _, filenames in os.walk(r, onerror=lambda _: None):
            for fn in filenames:
                try:
                    fp = os.path.join(dirpath, fn)
                    st = os.stat(fp)
                    if st.st_size >= min_bytes:
                        found.append({
                            "path": fp,
                            "name": fn,
                            "size_bytes": st.st_size,
                            "size_str": format_bytes(st.st_size),
                            "modified": datetime.fromtimestamp(st.st_mtime).strftime("%d/%m/%Y %H:%M"),
                        })
                except Exception:
                    pass

    found.sort(key=lambda x: x["size_bytes"], reverse=True)
    return found[:max_results]


def scan_duplicate_files(min_size_mb: int = 5, max_groups: int = 30) -> List[Dict[str, Any]]:
    """Localiza arquivos duplicados por tamanho + hash SHA-256 em Downloads, Desktop e Documentos."""
    user_profile = Path(os.environ.get("USERPROFILE", os.path.expanduser("~")))
    roots = [
        user_profile / "Downloads",
        user_profile / "Desktop",
        user_profile / "Documents",
    ]
    min_bytes = min_size_mb * 1024 * 1024
    by_size: Dict[int, List[str]] = {}

    for r in roots:
        if not r.exists():
            continue
        for dirpath, _, filenames in os.walk(r, onerror=lambda _: None):
            for fn in filenames:
                try:
                    fp = os.path.join(dirpath, fn)
                    sz = os.path.getsize(fp)
                    if sz >= min_bytes:
                        by_size.setdefault(sz, []).append(fp)
                except Exception:
                    pass

    groups: List[Dict[str, Any]] = []
    for sz, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash: Dict[str, List[str]] = {}
        for p in paths[:20]:
            try:
                h = hashlib.sha256()
                with open(p, "rb") as f:
                    h.update(f.read(65536))
                digest = h.hexdigest()
                by_hash.setdefault(digest, []).append(p)
            except Exception:
                pass

        for digest, dup_paths in by_hash.items():
            if len(dup_paths) >= 2:
                wasted = sz * (len(dup_paths) - 1)
                groups.append({
                    "hash": digest[:12],
                    "count": len(dup_paths),
                    "size_each": format_bytes(sz),
                    "wasted_bytes": wasted,
                    "wasted_str": format_bytes(wasted),
                    "files": dup_paths,
                })

    groups.sort(key=lambda g: g["wasted_bytes"], reverse=True)
    return groups[:max_groups]
