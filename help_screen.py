"""Full-screen control reference for the cockpit."""

import pygame

import core


SECTIONS = (
    ("GENERAL", (
        ("F1 / Ctrl+H", "Open / close this help screen"),
        ("F11", "Toggle fullscreen / windowed"),
        ("ESC", "Close help or quit the game"),
        ("MOUSE", "Activate any cockpit button"),
        ("SNAP", "Save the current cockpit screenshot"),
    )),
    ("NAVIGATION & VIEWS", (
        ("I / O / P", "Objects / orbit zones / mercator"),
        ("L / ; / '", "Mercator / navigation / war map"),
        ("N", "Cycle the primary display"),
    )),
    ("FLIGHT & SYSTEMS", (
        ("Z / X", "Increase / decrease hyperspace speed"),
        ("C / V", "Increase / decrease normal speed"),
        ("Q / W", "Probe operations / launch"),
        ("F2-F5 / Ctrl+1-4", "Set ship damage level 1 - 4"),
    )),
    ("COMBAT", (
        ("D / F / G", "Menu / grid / heading overlay"),
        ("H / J", "Target / line overlay"),
        ("M   ,   .   /", "Select a shield mode"),
        ("LEFT / RIGHT", "Select previous / next weapon"),
        ("RIGHT SHIFT", "Toggle target board"),
    )),
    ("COMMS & STATUS", (
        ("9 / 0 / -", "Messages / reports / combined feed"),
        ("1 - 8", "Latch the matching alert indicator"),
    )),
)


def _keycap(surface, rect, label):
    """Draw a compact key label with the cockpit's bevel treatment."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, core.BUTTON_FACE, rect, border_radius=3)
    pygame.draw.line(surface, core.BEVEL_LIGHT, rect.topleft, rect.topright)
    pygame.draw.line(surface, core.BEVEL_LIGHT, rect.topleft, rect.bottomleft)
    pygame.draw.line(surface, core.BEVEL_DARK, rect.bottomleft, rect.bottomright)
    pygame.draw.line(surface, core.BEVEL_DARK, rect.topright, rect.bottomright)
    core.fit_text(surface, label, rect.inflate(-10, -2), core.WHITE, 18)


def _section(surface, rect, title, rows):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, core.PANEL_BG, rect)
    pygame.draw.rect(surface, core.FRAME_DIM, rect, 1)

    title_rect = pygame.Rect(rect.x + 18, rect.y - 12, 0, 25)
    title_font = core.font(18, True)
    title_label = title_font.render(title, True, core.FRAME)
    title_rect.width = title_label.get_width() + 18
    pygame.draw.rect(surface, core.PANEL_BG, title_rect)
    surface.blit(title_label, (title_rect.x + 9, title_rect.y + 2))

    row_h = (rect.height - 34) / len(rows)
    key_w = min(210, rect.width * 0.36)
    for index, (key, description) in enumerate(rows):
        y = round(rect.y + 24 + index * row_h)
        key_rect = pygame.Rect(rect.x + 20, y + 4, key_w, min(32, row_h - 9))
        _keycap(surface, key_rect, key)
        text_rect = pygame.Rect(key_rect.right + 18, y, rect.right - key_rect.right - 34, row_h)
        core.fit_text(surface, description, text_rect, core.CYAN, 18, align="left")


def draw(surface):
    """Draw the help screen over the completed cockpit frame."""
    veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 238))
    surface.blit(veil, (0, 0))

    frame = pygame.Rect(150, 80, surface.get_width() - 300, surface.get_height() - 160)
    pygame.draw.rect(surface, core.PANEL_BG, frame)
    pygame.draw.rect(surface, core.FRAME, frame, 2)
    pygame.draw.rect(surface, core.FRAME_DIM, frame.inflate(-12, -12), 1)

    core.text_line(surface, "COMMAND REFERENCE", (surface.get_width() // 2, 112),
                   core.FRAME, 34, True, "center")
    core.text_line(surface, "KRELLAN BATTLECRUISER CONTROL SYSTEMS",
                   (surface.get_width() // 2, 154), core.GREY, 15, True, "center")
    pygame.draw.line(surface, core.FRAME_DIM, (190, 187), (1730, 187), 1)

    left = pygame.Rect(195, 220, 730, 285)
    right = pygame.Rect(995, 220, 730, 285)
    lower_left = pygame.Rect(195, 550, 730, 340)
    lower_right_top = pygame.Rect(995, 550, 730, 200)
    lower_right_bottom = pygame.Rect(995, 790, 730, 100)
    for rect, (title, rows) in zip(
            (left, right, lower_left, lower_right_top, lower_right_bottom), SECTIONS):
        _section(surface, rect, title, rows)

    core.text_line(surface, "F1 OR CTRL+H  CLOSE HELP", (surface.get_width() // 2, 935),
                   core.YELLOW, 18, True, "center")
