"""Shared theme, fonts, asset loading, and text helpers for the cockpit UI."""

import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
FONT_NAME = "couriernew"

# Console palette tuned to the gray Star Fleet II Deluxe command screen.
BLACK = (0, 0, 0)
SHELL_BG = (154, 154, 151)
PANEL_BG = (205, 203, 195)
FRAME = (238, 238, 232)
FRAME_DIM = (92, 92, 88)
BEVEL_LIGHT = (255, 255, 250)
BEVEL_DARK = (112, 112, 108)
BUTTON_FACE = (214, 213, 207)
BUTTON_ACTIVE = (64, 224, 34)
BUTTON_HOVER = (184, 226, 224)

CYAN = (0, 145, 142)
GREEN = (66, 225, 41)
RED = (190, 22, 28)
YELLOW = (245, 236, 82)
GREY = (96, 96, 94)
MAGENTA = (238, 26, 222)
WHITE = (232, 232, 226)

NAMED = {
    "cyan": CYAN, "green": GREEN, "red": RED, "yellow": YELLOW,
    "grey": GREY, "gray": GREY, "magenta": MAGENTA, "white": WHITE,
    "black": BLACK, "frame": FRAME, "panel": PANEL_BG,
}

_FONTS = {}
_ASSETS = {}


def color(value):
    """Resolve a name or tuple to a pygame Color."""
    if isinstance(value, str):
        return pygame.Color(NAMED.get(value.lower(), value))
    return pygame.Color(value)


def font(size, bold=True):
    """Return a cached font so surfaces are not rebuilt every frame."""
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = pygame.font.SysFont(FONT_NAME, size, bold)
    return _FONTS[key]


def asset(name):
    """Load an image from the assets folder, cached, with a visible fallback."""
    if name in _ASSETS:
        return _ASSETS[name]
    path = os.path.join(ASSET_DIR, name)
    try:
        surf = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        surf.fill((40, 40, 40))
        pygame.draw.rect(surf, FRAME, surf.get_rect(), 1)
    _ASSETS[name] = surf
    return surf


def fit_font(text, max_width, max_height, start_size, bold=True):
    """Pick the largest cached font whose render fits the given box."""
    size = start_size
    while size > 6:
        f = font(size, bold)
        if f.size(text)[0] <= max_width and f.get_height() <= max_height:
            return f
        size -= 1
    return font(6, bold)


def fit_text(surface, text, rect, fg, start_size=12, align="center",
             valign="center", bold=True):
    """Render text shrunk to fit rect so it never clips or overflows."""
    rect = pygame.Rect(rect)
    text = str(text)
    f = fit_font(text, rect.width - 2, rect.height, start_size, bold)
    label = f.render(text, True, color(fg))
    if label.get_width() > rect.width - 2:
        # Hard clip as a last resort once minimum font size is reached.
        clip = pygame.Rect(0, 0, rect.width - 2, label.get_height())
        label = label.subsurface(clip.clip(label.get_rect())).copy()
    pos = label.get_rect()
    pos.centerx = rect.centerx if align == "center" else pos.centerx
    if align == "left":
        pos.left = rect.left + 2
    elif align == "right":
        pos.right = rect.right - 2
    if valign == "center":
        pos.centery = rect.centery
    elif valign == "top":
        pos.top = rect.top + 1
    elif valign == "bottom":
        pos.bottom = rect.bottom - 1
    surface.blit(label, pos)
    return label.get_width()


def text_line(surface, text, pos, fg, size=12, bold=True, align="left"):
    """Blit a single line of text at a point without fitting."""
    label = font(size, bold).render(str(text), True, color(fg))
    rect = label.get_rect()
    setattr(rect, "topleft" if align == "left" else "midtop", pos)
    if align == "center":
        rect.center = pos
    surface.blit(label, rect)
    return rect
