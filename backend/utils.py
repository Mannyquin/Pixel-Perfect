"""
Utility functions for SVG Avatar System

Handles:
- SVG transforms (positioning, scaling)
- Color injection
- Layer wrapping
- Debug helpers
"""

import re


# -------------------------------
# 🎯 SVG TRANSFORMS
# -------------------------------

def apply_transform(svg: str, x: float = 0, y: float = 0, scale: float = 1.0) -> str:
    if x == 0 and y == 0 and scale == 1.0:
        return svg  # 🔥 DO NOT wrap if no transform

    return f'''
    <g transform="translate({x},{y}) scale({scale})">
        {svg}
    </g>
    '''


# -------------------------------
# 🎨 COLOR INJECTION
# -------------------------------

def inject_color(svg: str, color: str, placeholder: str = "{{skin_color}}") -> str:
    """
    Replaces placeholder with actual color

    Args:
        svg (str)
        color (str): hex color (e.g. #f2c7a5)
        placeholder (str)

    Returns:
        str
    """

    return svg.replace(placeholder, color)


def inject_multiple_colors(svg: str, color_map: dict) -> str:
    """
    Replace multiple placeholders

    Example:
        {
            "{{skin_color}}": "#f2c7a5",
            "{{hair_color}}": "#000000"
        }
    """

    for key, value in color_map.items():
        svg = svg.replace(key, value)

    return svg


# -------------------------------
# 🧼 SVG CLEANING
# -------------------------------

def remove_svg_wrapper(svg: str) -> str:
    """
    Removes outer <svg> tags if present
    (so it can be safely embedded as a layer)
    """

    svg = re.sub(r"<\s*svg[^>]*>", "", svg)
    svg = re.sub(r"<\s*/\s*svg\s*>", "", svg)

    return svg.strip()


def clean_svg(svg: str) -> str:
    """
    General cleanup:
    - remove extra whitespace
    - remove svg wrapper
    """

    svg = remove_svg_wrapper(svg)
    svg = svg.strip()

    return svg


# -------------------------------
# 🧱 LAYER COMPOSITION
# -------------------------------

def wrap_svg(layers: list) -> str:
    """
    Wraps multiple layers into final SVG

    Args:
        layers (list): list of SVG strings

    Returns:
        str: final SVG
    """

    return f"""
        <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">

        <defs>
            <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#f5f5f5"/>
                <stop offset="100%" stop-color="#e0e0e0"/>
            </linearGradient>
        </defs>

        <rect width="512" height="512" fill="url(#bgGrad)"/>

        {''.join(layers)}

        </svg>
        """


# -------------------------------
# 🧪 DEBUG HELPERS
# -------------------------------

def debug_layer(name: str, svg: str) -> str:
    """
    Adds a debug label inside SVG layer
    """

    return f"""
    <g id="{name}">
        {svg}
    </g>
    """


def print_svg_preview(svg: str, length: int = 500):
    """
    Prints part of SVG for debugging
    """

    print("🔍 SVG Preview:")
    print(svg[:length] + ("..." if len(svg) > length else ""))


# -------------------------------
# 🛠 SAFE OPERATIONS
# -------------------------------

def safe_svg(svg: str) -> str:
    """
    Ensures SVG string is not None or empty
    """

    if not svg:
        return ""

    return svg.strip()


# -------------------------------
# 🎨 DEFAULT COLORS
# -------------------------------

DEFAULT_COLORS = {
    "skin": "#f2c7a5",
    "hair": "#2c2c2c",
    "eyes": "#000000",
}