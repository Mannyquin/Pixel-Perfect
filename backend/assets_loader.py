

import os


# Base path 
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))


class AssetNotFoundError(Exception):
    """Custom error for missing SVG assets"""
    pass


def build_path(style: str, category: str, name: str) -> str:
    """
    Builds full file path for an asset

    Example:
    style = "anime"
    category = "hair/front"
    name = "short"

    → backend/assets/anime/hair/front/short.svg
    """

    return os.path.join(BASE_PATH, style, category, f"{name}.svg")


def load_svg(style: str, category: str, name: str) -> str:
    """
    Loads an SVG file as string

    Args:
        style (str): e.g., "anime"
        category (str): e.g., "face", "eyes", "hair/front"
        name (str): file name without extension

    Returns:
        str: SVG content
    """

    path = build_path(style, category, name)

    if not os.path.exists(path):
        raise AssetNotFoundError(
            f"❌ Asset not found: style='{style}', category='{category}', name='{name}'\nPath: {path}"
        )

    try:
        with open(path, "r", encoding="utf-8") as file:
            svg_content = file.read()
    except Exception as e:
        raise RuntimeError(f"Error reading SVG file: {path}\n{str(e)}")

    return svg_content



_CACHE = {}


def load_svg_cached(style: str, category: str, name: str) -> str:
    """
    Cached version of load_svg (improves performance)
    """

    key = f"{style}:{category}:{name}"

    if key in _CACHE:
        return _CACHE[key]

    svg = load_svg(style, category, name)
    _CACHE[key] = svg

    return svg



def list_available_assets(style: str, category: str):
    """
    Lists all available assets in a folder
    """

    folder_path = os.path.join(BASE_PATH, style, category)

    if not os.path.exists(folder_path):
        print(f"⚠️ Folder does not exist: {folder_path}")
        return []

    files = [
        f.replace(".svg", "")
        for f in os.listdir(folder_path)
        if f.endswith(".svg")
    ]

    return files



def safe_load_svg(style: str, category: str, name: str, fallback: str = None) -> str:
    """
    Loads SVG safely with fallback option

    Example:
    safe_load_svg("anime", "eyes", "angry", fallback="neutral")
    """

    try:
        return load_svg(style, category, name)
    except AssetNotFoundError:
        if fallback:
            print(f"⚠️ Falling back to '{fallback}' for {category}")
            return load_svg(style, category, fallback)
        else:
            raise