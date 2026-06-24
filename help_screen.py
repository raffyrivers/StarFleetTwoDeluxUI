"""Full-screen control reference for the cockpit."""

import pygame

import core

HELP_BG = (16, 18, 18)
HELP_PANEL = (28, 31, 31)
HELP_PANEL_ALT = (36, 39, 38)
HELP_BORDER = (214, 213, 207)
HELP_TEXT = (230, 232, 222)
HELP_MUTED = (166, 170, 164)


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
    core.fit_text(surface, label, rect.inflate(-10, -2), core.BLACK, 18)


def _section(surface, rect, title, rows):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, HELP_PANEL, rect)
    pygame.draw.rect(surface, HELP_BORDER, rect, 1)
    pygame.draw.rect(surface, core.FRAME_DIM, rect.inflate(-6, -6), 1)

    title_rect = pygame.Rect(rect.x + 18, rect.y - 13, 0, 26)
    title_font = core.font(18, True)
    title_label = title_font.render(title, True, core.GREEN)
    title_rect.width = title_label.get_width() + 20
    pygame.draw.rect(surface, HELP_PANEL, title_rect)
    pygame.draw.rect(surface, HELP_BORDER, title_rect, 1)
    surface.blit(title_label, (title_rect.x + 10, title_rect.y + 3))

    body_top = rect.y + 28
    body_height = rect.height - 42
    row_h = max(34, body_height // len(rows))
    key_w = min(230, int(rect.width * 0.36))
    for index, (key, description) in enumerate(rows):
        row = pygame.Rect(rect.x + 16, body_top + index * row_h, rect.width - 32, row_h)
        if index % 2:
            pygame.draw.rect(surface, HELP_PANEL_ALT, row)
        key_rect = pygame.Rect(row.x + 8, row.y + (row_h - 28) // 2, key_w, 28)
        _keycap(surface, key_rect, key)
        text_rect = pygame.Rect(key_rect.right + 22, row.y, row.right - key_rect.right - 28, row_h)
        core.fit_text(surface, description, text_rect, HELP_TEXT, 18, align="left")


def draw(surface):
    """Draw the help screen over the completed cockpit frame."""
    veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 210))
    surface.blit(veil, (0, 0))

    frame = pygame.Rect(150, 80, surface.get_width() - 300, surface.get_height() - 160)
    pygame.draw.rect(surface, HELP_BG, frame)
    pygame.draw.rect(surface, HELP_BORDER, frame, 2)
    pygame.draw.rect(surface, core.FRAME_DIM, frame.inflate(-12, -12), 1)

    core.text_line(surface, "COMMAND REFERENCE", (surface.get_width() // 2, 112),
                   core.GREEN, 34, True, "center")
    core.text_line(surface, "KRELLAN BATTLECRUISER CONTROL SYSTEMS",
                   (surface.get_width() // 2, 154), HELP_MUTED, 15, True, "center")
    pygame.draw.line(surface, HELP_BORDER, (190, 187), (1730, 187), 1)

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
