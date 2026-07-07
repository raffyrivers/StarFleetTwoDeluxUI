"""Builds every console panel and draws its per-frame content.

Layout coordinates match the Star Fleet II Deluxe command screen. Static
readouts are expressed as data and rendered through shared helpers so text
always fits its box and the code stays compact.
"""

import math
import random
import pygame
import core
from core import (BLACK, PANEL_BG, FRAME, FRAME_DIM, BUTTON_FACE, CYAN, GREEN,
                  RED, YELLOW, GREY, MAGENTA, WHITE, color, font, fit_text,
                  text_line, asset)
from widgets import Panel, Button, Text, Display, CircleDisplay, StatusBar
from video import VideoDisplay

P = {}            # panels keyed by tab/name
WARN_WORDS = {"CAUTION", "LOW", "HOLD", "QUEUED", "LOCK"}

# Communication feed content (authentic Krellan briefing data).
MESSAGES = [
    ("Executive Off.", "Klagar-class battlecruiser ready"),
    ("Starfort SF-1", "24 torps / 4000 power loaded"),
    ("Fleet Command", "training patrol assigned"),
    ("Damage Control", "shields and tractor beam nominal"),
    ("Probe Control", "L:5 S:5 sensor probes loaded"),
    ("Landing Party", "150 shock troops aboard"),
    ("Strategic Cmd", "4 destroyer escorts standing by"),
]
REPORTS = [
    ("NAV-006", "docked at region 6,0"),
    ("ENG-4000", "power reserve 4000 units"),
    ("CMB-024", "torpedo stores full"),
    ("DATA-1000", "supplies 1000 tons"),
    ("TRP-150", "shock troops ready"),
    ("SCI-L5S5", "sensor probes loaded"),
    ("STG-004", "destroyer escort screen"),
]


# --- shared display helpers -------------------------------------------------

def text_rows(surface, rows, x=6, y=6, line_h=14, size=10):
    for text, fg in rows:
        fit_text(surface, text, [x, y, surface.get_width() - x - 4, line_h],
                 fg, size, align="left")
        y += line_h


def readout(surface, rows, x=6, y=6, line_h=15, size=11, label_w=82):
    for label, value, fg in rows:
        fit_text(surface, label, [x, y, label_w, line_h], CYAN, size, align="left")
        if value != "":
            fit_text(surface, value, [x + label_w + 6, y,
                     surface.get_width() - x - label_w - 10, line_h],
                     fg, size, align="left")
        y += line_h


def table(surface, headers, rows, x, y, widths, line_h=14, size=10, column_lines=False):
    surf_rect = surface.get_rect()
    cx = x
    for i, head in enumerate(headers):
        fit_text(surface, head, [cx, y, widths[i] - 2, line_h], CYAN, size, align="center")
        cx += widths[i]
        if column_lines:
            pygame.draw.line(surface, GREY, (cx, 0), (cx, surf_rect.h))
    pygame.draw.line(surface, FRAME, (0, y + line_h), (surf_rect.w + sum(widths), y + line_h), 1)
    for r, row in enumerate(rows):
        cx = x
        ry = y + line_h + 3 + r * line_h
       
        for i, cell in enumerate(row):
            fg = YELLOW if cell in WARN_WORDS else GREEN
            fit_text(surface, cell, [cx, ry, widths[i] - 2, line_h], fg, size, align="left")
            
            cx += widths[i]


# --- panel construction -----------------------------------------------------

def build():
    P.clear()
    layout = [
       (10, 30, 440, 330, "Navigation Console", 168, True),
        (455, 30, 192, 225, "Science Console", 130, True),
        (656, 50, 655, 385, "Primary Display", 130, True),
        (1330, 30, 440, 60, "Status Indicators", 140, True),
        (451, 265, 197, 170, "Navigation", 0, True),
        (10, 361, 440, 225, "Star Map", 0, False),
        (1330, 110, 580, 260, "Computer Display", 140, True),
        (451, 451, 197, 135, "Data", 60, True),
        (660, 455, 655, 550, "Combat Console", 130, True),
        (1330, 390, 580, 350, "Strategic Command Console", 200, True),
        (10, 605, 640, 240, "Engineering Console", 160, True),
        (10, 865, 640, 205, "Communication Console", 180, True),
        (1330, 760, 330, 310, "Security Console", 130, True),
        (1670, 760, 240, 310, "Commanders Log", 150, True),
    ]
    for x, y, w, h, label, tab, has_tab in layout:
        P[label] = Panel(x, y, w, h, label, tab, has_tab)

    _build_primary()
    _build_science()
    _build_navigation()
    _build_navigation_data()
    _build_star_map()
    _build_status_indicators()
    _build_computer()
    _build_data()
    _build_engineering()
    _build_communication()
    _build_combat()
    _build_strategic()
    _build_security()
    _build_log()
    return list(P.values())


def _build_primary():
    panel = P["Primary Display"]
    video = VideoDisplay(panel, "primary", (panel.width - 10, 320), (5, 5))
    video.set_videos(["DeepSpace.mp4", "EarthOrbit.mp4"])
    video.fallback.label = "EARTH ORBIT"
    if len(video.sources) > 1:
        video.index = 1
    Text(panel, (5, 350), "Msn Elapsed", "cyan", 11)
    panel.lbl_elapsed = pygame.Rect(95, 344, 84, 18)
    Text(panel, (190, 350), "Time Left", "cyan", 11)
    panel.lbl_left = pygame.Rect(255, 344, 84, 18)
    right_x = panel.width - 295
    Button(panel, (right_x, 333, 64, 18), "REST", text_size=11)
    Button(panel, (right_x, 356, 64, 18), "Sim Freeze", text_size=11)
    Button(panel, (right_x + 70, 356, 105, 18), "Help F1/Ctrl+H", text_size=10)


def _build_science():
    panel = P["Science Console"]
    CircleDisplay(panel, "scope", (12, 36), 84)
    Button(panel, (148, 30, 36, 18), "SRS", text_size=11)
    Button(panel, (12, 196, 72, 18), "Dept Q", group="science_page",
           active=True, text_size=11)
    Button(panel, (96, 196, 88, 18), "Planet Data", group="science_page", text_size=11)


def _build_navigation():
    panel = P["Navigation Console"]
    Display(panel, "orbit", (210, 210), (5, 24))
    Display(panel, "system", (210, 210), (225, 24))
    Display(panel, "orbital display", (210, 80), (5, 245))
    Display(panel, "planets display", (210, 80), (225, 245))
    Text(panel, (5, 8), "Orbital Displays", "cyan", 11)
    Text(panel, (228, 8), "System Map", "cyan", 11)
    Text(panel, (305, 233), "Planets", BLACK, 11)
    Button(panel, (7, 233, 67, 13), "Objects", key=pygame.K_i, group="nav",
           active=True, text_size=11)
    Button(panel, (77, 233, 67, 13), "Orbit Zones", key=pygame.K_o, group="nav", text_size=11)
    Button(panel, (147, 233, 67, 13), "Mercator Map", key=pygame.K_p, group="nav", text_size=11)


def _build_navigation_data():
    panel = P["Navigation"]
    Display(panel, "nav readout", (192, 145), (2, 22), double_border=False)
    Button(panel, (122, 62, 66, 18), "Evasive", key=pygame.K_e, text_size=12)
    Button(panel, (126, 94, 28, 22), "<<", text_size=16)
    Button(panel, (160, 94, 28, 22), ">>", text_size=16)


def _build_star_map():
    panel = P["Star Map"]
    Display(panel, "map", (430, 196), (5, 24))
    Button(panel, (206, 4, 90, 16), "Mercator Map", key=pygame.K_l, group="map", text_size=11)
    Button(panel, (300, 4, 62, 16), "Nav Map", key=pygame.K_SEMICOLON, group="map", text_size=11)
    Button(panel, (366, 4, 66, 16), "War Map", key=pygame.K_QUOTE, group="map", text_size=11)


def _build_status_indicators():
    panel = P["Status Indicators"]
    for i in range(10):
        col = i % 5
        row = i // 5
        x = 10 + col * 60
        y = 4 + row * 28
        Text(panel, (x + 18, y), str(i + 1), "cyan", 11)
        panel.add(_Indicator(panel, (x, y + 12, 40, 12), good=True))
    Button(panel, (312, 22, 30, 18), "\u2640", text_size=12)
    Button(panel, (312, 42, 50, 16), "SNAP", text_size=11)
    Text(panel, (352, 8), "Distance", "cyan", 11)
    panel.lbl_distance = pygame.Rect(352, 22, 62, 16)


class _Indicator:
    """Small green/red status lamp."""

    def __init__(self, panel, rect, good=True):
        self.panel = panel
        self.rect = pygame.Rect(rect)
        self.good = good
        self.label = None
        self.z = 2

    def prepare(self):
        pass

    def draw(self):
        pygame.draw.rect(self.panel.surf, GREEN if self.good else RED, self.rect)
        pygame.draw.rect(self.panel.surf, FRAME_DIM, self.rect, 1)


def _build_computer():
    panel = P["Computer Display"]
    menu = ["Combat Stats", "Information", "Landing Party", "Planets", "Star Systems",
            "Bases", "Intelligence", "Reference Lib", "Self-Destruct", "Special Services"]
    Display(panel, "options", (90, 250), (5, 5))
    Display(panel, "screen", (475, 250), (100, 5))

    menu_x, menu_y, menu_w, menu_h, menu_gap = 8, 7, 84, 22, 3
    for i, label in enumerate(menu):
        Button(panel, (menu_x, menu_y + i * (menu_h + menu_gap), menu_w, menu_h),
               label, group="computer_menu", active=label == "Star Systems", text_size=10)

def _build_data():
    panel = P["Data"]
    Display(panel, "stores", (192, 112), (2, 20), double_border=False)


def _build_engineering():
    panel = P["Engineering Console"]
    Display(panel, "probes", (380, 98), (5, 25))
    Display(panel, "energy", (380, 90), (5, 145))
    Display(panel, "velocity", (250, 210), (386, 25))
    Text(panel, (5, 8), "Probes Control", "cyan", 12)
    Text(panel, (400, 8), "Damage - Ship", "cyan", 12)
    Text(panel, (560, 8), "Velocity", "cyan", 12)
    Text(panel, (5, 128), "Energy", "cyan", 12)
    Button(panel, (214, 6, 88, 17), "Operations", key=pygame.K_q, group="probe", text_size=12)
    Button(panel, (306, 6, 78, 17), "Launch", key=pygame.K_w, group="probe", text_size=12)


def _build_communication():
    panel = P["Communication Console"]
    Display(panel, "feed left", (315, 175), (5, 25))
    Display(panel, "feed right", (310, 175), (325, 25))
    Text(panel, (5, 9), "Status", "cyan", 12)
    Button(panel, (325, 7, 70, 16), "Messages", key=pygame.K_9, group="comm",
           active=True, text_size=12)
    Button(panel, (399, 7, 62, 16), "Reports", key=pygame.K_0, group="comm", text_size=12)
    Button(panel, (465, 7, 74, 16), "Combined", key=pygame.K_MINUS, group="comm", text_size=12)
    Button(panel, (543, 7, 92, 16), "Send Message", text_size=12)


def _build_combat():
    panel = P["Combat Console"]
    Display(panel, "grid", (470, 470), (5, 25))
    Text(panel, (5, 6), "Combat Information Display", "cyan", 11)
    Text(panel, (515, 6), "Alignment:", BLACK, 11)
    Button(panel, (586, 3, 38, 20), "BCS", group="combat_align", active=True, text_size=11)
    Button(panel, (628, 3, 38, 20), "SCS", group="combat_align", text_size=11)
    Button(panel, (40, 510, 44, 20), "Menu", key=pygame.K_d, group="cmb_menu", text_size=11)
    Button(panel, (90, 510, 44, 20), "Grid", key=pygame.K_f, group="cmb_grid", text_size=11)
    Button(panel, (140, 510, 44, 20), "Head", key=pygame.K_g, group="cmb_head", text_size=11)
    Button(panel, (190, 510, 44, 20), "Target", key=pygame.K_h, group="cmb_tgt", text_size=11)
    Button(panel, (240, 510, 44, 20), "Line", key=pygame.K_j, group="cmb_line", text_size=11)
    # Make these momentary toggles so a click flips them independently.
    for b in panel.elements:
        if isinstance(b, Button) and b.group and b.group.startswith("cmb_"):
            b.group = None
    # Shield mode radio buttons sit on the shields sub-panel.
    Button(panel, (493, 304, 74, 16), "Auto", key=pygame.K_m, group="shield", text_size=10)
    Button(panel, (573, 304, 74, 16), "Manual", key=pygame.K_COMMA, group="shield",
           active=True, text_size=10)
    Button(panel, (493, 322, 74, 16), "Battle Entry", key=pygame.K_PERIOD,
           group="shield", text_size=10)
    Button(panel, (573, 322, 74, 16), "Maximum", key=pygame.K_SLASH,
           group="shield", text_size=10)
    for i, name in enumerate(("Phaser", "Trp1", "Trp2", "ObltrPd")):
        Button(panel, (493 + i * 39, 55, 37, 18), name, group="combat_weapon",
               active=i == 0, text_size=10)
    Button(panel, (610, 92, 34, 18), "ECM", text_size=10)
    for i, name in enumerate(("Ph", "T1", "T2", "Cont")):
        Button(panel, (493 + i * 39, 353, 37, 30), name, group="weapon_condition",
               active=i == 0, text_size=10)
    Button(panel, (596, 398, 50, 18), "Board", key=pygame.K_RSHIFT, text_size=10)


def _build_strategic():
    panel = P["Strategic Command Console"]
    Display(panel, "escort", (150, 120), (5, 12))
    Display(panel, "formation", (80, 120), (165, 12))
    Display(panel, "fleet pos", (200, 120), (255, 12))
    Display(panel, "fleet cmd", (570, 195), (5, 150))
    cmd_x, cmd_w, cmd_h = 455, 120, 20
    for y, label in ((10, "Escort Commands"), (39, "Fleet Commands"),
                     (68, "Strategic Commands"), (97, "Menu")):
        Button(panel, (cmd_x, y, cmd_w, cmd_h), label, text_size=10)
    Button(panel, (cmd_x, 126, 58, cmd_h), "Editor", text_size=10)
    Button(panel, (cmd_x + 62, 126, 58, cmd_h), "View", text_size=10)

def _toggle_security_board(panel, state):
    if panel.security_mode == "boarding":
        _draw_boarding_panel(panel, state)
    else:
        _draw_security_panel(panel, state)

def _draw_security_panel(panel, state):
    internal = panel.get("internal")
    interrogations = panel.get("interrogations")
    internal.surf.fill(BLACK)
    interrogations.surf.fill(BLACK)

    fit_text(internal.surf, f"Shock Troops: {state.shock_troops}", [6, 20, 200, 16], GREEN, 12)
    fit_text(internal.surf, f"Prisoners: {state.prisoners}", [6, 40, 200, 16], GREEN, 12)
    fit_text(internal.surf, f"Target: {state.selected_target['name'][:18]}",
             [6, 66, 260, 16], CYAN, 12, align="left")
    fit_text(interrogations.surf, "QUEUE", [8, 8, 80, 14], CYAN, 10, align="left")
    fit_text(interrogations.surf, "No active interviews" if state.prisoners == 0 else "KR-17 00:12 hold",
             [8, 27, 190, 14], YELLOW if state.prisoners else GREEN, 10, align="left")

def _draw_boarding_panel(panel, state):
    internal = panel.get("internal")
    interrogations = panel.get("interrogations")
    internal.surf.fill(BLACK)
    interrogations.surf.fill(BLACK)
    ctx = state.boarding_context()

    img_h = internal.size[1] - 40
    img_w = internal.size[0]
    img = pygame.transform.smoothscale(panel.boarding_img, (img_w, img_h))
    internal.surf.blit(img, (0,0))

    # --- table under the image ---
    list_y = img_h - 12  # adjust vertical position
    label_x = 12  # red label position
    value_x = 90  # green value position

    enemType = "battlecruiser"
    enemClass = "klagar"


    rows = [
        ("TYPE", enemType.upper()),
        ("CLASS", enemClass.upper()),
        ("CREW", f"{ctx['defenders']}   SHK: {ctx['shock_troops']}"),
    ]

    for i, (label, value) in enumerate(rows):
        line_y = list_y + i * 18  # spacing between lines

        # red label
        fit_text(internal.surf,
                 f"{label}:",
                 [label_x, line_y, 80, 14],
                 RED, 11, align="left")

        # green value on same line
        fit_text(internal.surf,
                 value,
                 [value_x, line_y, 200, 14],
                 GREEN, 11, align="left")

    _draw_boarding_notes(interrogations.surf, ctx)


def _draw_boarding_notes(surface, ctx):
    fit_text(surface, "BOARDING DATA", [8, 6, 130, 14], CYAN, 11, align="left")
    notes = [
        ("Target shields must be down.", RED if ctx["shields_up"] else GREEN),
        (f"Enemy prisoners aboard: {ctx['prisoners']}", YELLOW if ctx["prisoners"] else GREEN),
        (f"Defenders remaining: {ctx['defenders']}", RED if ctx["defenders"] else GREEN),
        (ctx["status"], RED if "BLOCKED" in ctx["status"] or not ctx["valid"] else GREEN),
    ]
    for i, (text, fg) in enumerate(notes):
        fit_text(surface, text, [8, 28 + i * 17, 300, 14], fg, 10, align="left")


def _build_security():
    panel = P["Security Console"]
    panel.security_mode = "security"
    panel.boarding_img = asset("SFD_Enemy_Ship.png")

    # boarding button
    Button(panel, (5,22,90,18), "Boarding", text_size=12,
   on_toggle=lambda b: setattr(panel, "security_mode",
   "boarding" if b.active else "security"))

    Display(panel, "internal", (320, 160), (5, 18))
    Display(panel, "interrogations", (320, 100), (5, 205))
    Text(panel, (5, 190), "Interrogations", "cyan", 12)


def _build_log():
    panel = P["Commanders Log"]
    Display(panel, "log", (228, 298), (5, 6))


# --- per-frame drawing ------------------------------------------------------

def draw(state, current_time):
    _draw_primary(state)
    _draw_science(state)
    _draw_navigation(state)
    _draw_navigation_console_data(state)
    _draw_navigation_data(state)
    _draw_star_map(state)
    _draw_status_indicators(state)
    _draw_computer(state)
    _draw_data(state)
    _draw_engineering(state)
    _draw_communication(state, current_time)
    _draw_combat(state)
    _draw_strategic(state)
    _toggle_security_board(P["Security Console"], state)
    _draw_log(state)

def _draw_primary(state):
    panel = P["Primary Display"]
    pygame.draw.rect(panel.surf, BLACK, panel.lbl_elapsed)
    pygame.draw.rect(panel.surf, FRAME_DIM, panel.lbl_elapsed, 1)
    fit_text(panel.surf, f"{state.mission_elapsed_days:.2f} Days", panel.lbl_elapsed, GREEN, 13)
    pygame.draw.rect(panel.surf, BLACK, panel.lbl_left)
    pygame.draw.rect(panel.surf, FRAME_DIM, panel.lbl_left, 1)
    fit_text(panel.surf, f"{state.time_left_days:.2f} Days", panel.lbl_left, GREEN, 13)
    status = pygame.Rect(panel.width - 115, 333, 100, 40)
    status_col = {"Green": GREEN, "Yellow": YELLOW, "Red": RED}.get(state.alert_status, GREEN)
    pygame.draw.rect(panel.surf, status_col, status)
    fit_text(panel.surf, f"Status: {state.alert_status}", status, BLACK, 13)


def _draw_science(state):
    panel = P["Science Console"]
    scope = panel.get("scope")
    scope.surf.fill(PANEL_BG)
    cx, cy = scope.rect.center
    radius = scope.radius - 1
    pygame.draw.circle(scope.surf, BLACK, (cx, cy), radius)

    def clipped_line_horizontal(y, col=WHITE, width=2):
        half = int(math.sqrt(max(0, radius * radius - (y - cy) ** 2)))
        pygame.draw.line(scope.surf, col, (cx - half, y), (cx + half, y), width)

    def clipped_line_vertical(x, col=WHITE, width=2):
        half = int(math.sqrt(max(0, radius * radius - (x - cx) ** 2)))
        pygame.draw.line(scope.surf, col, (x, cy - half), (x, cy + half), width)

    clipped_line_horizontal(cy)
    clipped_line_vertical(cx)
    for tick in range(-3, 4):
        if tick == 0:
            continue
        tx = cx + tick * 24
        ty = cy + tick * 24
        if abs(tx - cx) < radius:
            pygame.draw.line(scope.surf, WHITE, (tx, cy - 9), (tx, cy + 9), 2)
        if abs(ty - cy) < radius:
            pygame.draw.line(scope.surf, WHITE, (cx - 9, ty), (cx + 9, ty), 2)

    range_units = 8 if state.science_scope == "SRS" else 18
    scale = (radius - 8) / range_units
    contacts = state.scanner_contacts()
    if state.science_page == "Planet Data":
        contacts = [contact for contact in contacts if contact["kind"] == "planet"]
    for contact in contacts:
        dx = int((contact["x"] - state.system_x) * 5)
        dy = int((contact["y"] - state.system_y) * 5)
        if math.hypot(dx / 5, dy / 5) > range_units:
            continue
        px = int(cx + (contact["x"] - state.system_x) * scale)
        py = int(cy + (contact["y"] - state.system_y) * scale)
        dot = RED if contact.get("threat") else GREEN
        pygame.draw.circle(scope.surf, dot, (px, py), 3)
    heading = math.radians(state.actual_heading - 90)
    ship = [
        (cx + int(math.cos(heading) * 10), cy + int(math.sin(heading) * 10)),
        (cx + int(math.cos(heading + 2.45) * 8), cy + int(math.sin(heading + 2.45) * 8)),
        (cx + int(math.cos(heading - 2.45) * 8), cy + int(math.sin(heading - 2.45) * 8)),
    ]
    pygame.draw.polygon(scope.surf, RED, ship)
    pygame.draw.circle(scope.surf, WHITE, (cx, cy), radius, 2)

    fit_text(panel.surf, state.science_scope, [10, 20, 52, 16], BLACK, 16, align="left")
    page_rect = pygame.Rect(68, 20, 76, 16)
    fg = CYAN if state.science_page == "Dept Q" else GREEN
    fit_text(panel.surf, state.science_page, page_rect, fg, 9, align="right")


def _draw_navigation(state):
    panel = P["Navigation Console"]
    orbit = panel.get("orbit")
    system = panel.get("system")
    for disp in (orbit, system):
        disp.surf.fill(BLACK)
        grid = pygame.Surface(disp.size, pygame.SRCALPHA)
        for gx in range(0, disp.rect.width, 21):
            pygame.draw.line(grid, (255, 255, 255, 40), (gx, 0), (gx, disp.rect.height))
        for gy in range(0, disp.rect.height, 21):
            pygame.draw.line(grid, (255, 255, 255, 40), (0, gy), (disp.rect.width, gy))
        disp.surf.blit(grid, (0, 0))
    ocx, ocy = orbit.rect.center
    for radius, ring_color in [(86, (20, 32, 68)), (62, (26, 38, 88)),
                               (42, (24, 70, 42)), (34, (30, 150, 54))]:
        pygame.draw.circle(orbit.surf, ring_color, (ocx, ocy), radius, 2)
    pygame.draw.circle(orbit.surf, (24, 88, 150), (ocx, ocy), 23)
    pygame.draw.ellipse(orbit.surf, (40, 148, 65), (ocx - 13, ocy - 10, 18, 10))
    pygame.draw.ellipse(orbit.surf, (52, 165, 75), (ocx + 2, ocy + 2, 14, 9))
    pygame.draw.arc(orbit.surf, (160, 180, 210), (ocx - 21, ocy - 17, 42, 34), 0.4, 2.8, 1)
    cx, cy = system.rect.center
    pygame.draw.circle(system.surf, RED, (cx, cy), 90, 1)
    pygame.draw.circle(system.surf, (60, 120, 220), (cx, cy), 55, 1)
    pygame.draw.circle(system.surf, YELLOW, (cx, cy), 8)
    for contact in state.tactical_contacts():
        sx = int(cx + (contact["x"] - state.system_x) * 5)
        sy = int(cy + (contact["y"] - state.system_y) * 5)
        if 3 <= sx <= system.rect.width - 3 and 3 <= sy <= system.rect.height - 3:
            dot = RED if contact.get("threat") else ((255, 150, 60) if contact["kind"] == "planet" else CYAN)
            pygame.draw.circle(system.surf, dot, (sx, sy),
                               5 if contact["id"] == state.selected_target["id"] else 4)
            text_line(system.surf, contact["name"][:8], (sx - 20, sy - 16), dot, 8)
    ship_x = max(4, min(system.rect.width - 4, int(cx + (state.system_x - 40) * 2)))
    ship_y = max(4, min(system.rect.height - 4, int(cy + (state.system_y - 23) * 2)))
    pygame.draw.circle(system.surf, GREEN, (ship_x, ship_y), 4)
    for label, dx, dy in [("N", cx, 10), ("S", cx, disp.rect.height - 10),
                          ("E", disp.rect.width - 12, cy), ("W", 12, cy)]:
        text_line(orbit.surf, label, (dx, dy), CYAN, 10, align="center")


def _draw_navigation_console_data(state):
    panel = P["Navigation Console"] 
    orbit = panel.get("orbital display")
    planet = panel.get("planets display")
    orbit.surf.fill(BLACK)
    object_columns = ["ID#", "Name", "Rel-Pos", "Status"]
    zone_columns = ["ID#", "Zone", "Rel-Pos", "Status"]
    planets_columns = ["ID", "Cls", "Inh", "Tch", "LP", "BS", "Status"]
    obj_rows = []
    zone_rows = []
    planet_rows = []
    obj_col_widths = [35, 45, 40, 80]
    planets_col_widths = [25, 25, 25, 25, 25, 25, 50]
    
    contacts = state.scanner_contacts()
    for contact in contacts[:4]:
        rel = f"{round(contact['x'] - state.system_x)},{round(contact['y'] - state.system_y)}"
        status = "THREAT" if contact.get("threat") else "CLEAR"
        obj_rows.append([contact["id"], contact["name"][:8], rel, status])
        zone = "Mine" if contact["kind"] == "mine" else ("Orbit" if contact["kind"] == "planet" else "Track")
        zone_rows.append([contact["id"], zone, rel, status])
        if contact["kind"] == "planet":
            planet_rows.append([contact["id"][:2], "M", "Y", "4", "1", "0", "Survey"])

    active = next((b for b in panel.elements
                   if isinstance(b, Button) and b.active), None)
    if active and active.label == "Objects":
        table(orbit.surf, object_columns, obj_rows, 6, 5, obj_col_widths, column_lines=True)
    elif active and active.label == "Orbit Zones":
        table(orbit.surf, zone_columns, zone_rows, 6, 5, obj_col_widths, column_lines=True)

    table(planet.surf, planets_columns, planet_rows, 6, 5, planets_col_widths, column_lines=True) 


def _draw_navigation_data(state):
    disp = P["Navigation"].get("nav readout")
    disp.surf.fill((34, 34, 34))
    pygame.draw.rect(disp.surf, FRAME, disp.rect, 2)

    def field(rect, value, size=13, align="right"):
        rect = pygame.Rect(rect)
        pygame.draw.rect(disp.surf, BLACK, rect)
        pygame.draw.rect(disp.surf, WHITE, rect, 2)
        fit_text(disp.surf, value, rect.inflate(-4, -2), GREEN, size, align=align)

    fit_text(disp.surf, "X", [65, 4, 24, 14], CYAN, 11, align="center")
    fit_text(disp.surf, "Y", [94, 4, 24, 14], CYAN, 11, align="center")

    fit_text(disp.surf, "Reg. Loc:", [6, 20, 60, 15], CYAN, 10, align="left")
    field([62, 17, 28, 18], state.nav_region[0], 13)
    field([94, 17, 28, 18], state.nav_region[1], 13)
    fit_text(disp.surf, "Dist:", [128, 20, 28, 15], CYAN, 9, align="left")
    field([160, 17, 28, 18], f"{state.nav_distance:.1f}", 10)

    fit_text(disp.surf, "Orb Pos:", [6, 41, 60, 15], CYAN, 10, align="left")
    field([62, 38, 28, 18], state.nav_orbit[0], 13)
    field([94, 38, 28, 18], state.nav_orbit[1], 13)

    fit_text(disp.surf, "Course:", [6, 64, 58, 15], CYAN, 10, align="left")
    field([70, 61, 50, 18], state.nav_course, 13)
    fit_text(disp.surf, "Sideslip", [128, 58, 60, 12], CYAN, 8, align="center")

    fit_text(disp.surf, "Target 1:", [6, 86, 65, 15], CYAN, 10, align="left")
    field([70, 83, 50, 18], f"{state.nav_target[0]}, {state.nav_target[1]}", 11)
    fit_text(disp.surf, str(state.nav_sideslip), [144, 118, 28, 12], GREEN, 8, align="center")

    fit_text(disp.surf, "Object:", [6, 108, 52, 15], CYAN, 10, align="left")
    field([58, 105, 130, 18], state.nav_object, 11, align="center")

    fit_text(disp.surf, "Mode:", [6, 129, 52, 14], CYAN, 10, align="left")
    mode_rect = pygame.Rect(58, 125, 130, 18)
    pygame.draw.rect(disp.surf, BLACK, mode_rect)
    pygame.draw.rect(disp.surf, GREEN, mode_rect, 2)
    fit_text(disp.surf, state.nav_mode, mode_rect.inflate(-4, -2), GREEN, 12, align="center")

def _draw_star_map(state):
    panel = P["Star Map"]
    disp = panel.get("map")
    active = next((b for b in panel.elements
                   if isinstance(b, Button) and b.active), None)
    if active and active.label == "Nav Map":
        img = pygame.transform.smoothscale(asset("NavMap.png"), disp.size)
        disp.surf.blit(img, (0, 0))
    elif active and active.label == "War Map":
        img = pygame.transform.smoothscale(asset("WarMap.png"), disp.size)
        disp.surf.blit(img, (0, 0))
    else:
        rng = random.Random(74216)
        for _ in range(260):
            x = rng.randrange(8, disp.rect.width - 8)
            y = rng.randrange(14, disp.rect.height - 8)
            shade = rng.randrange(40, 150)
            disp.surf.set_at((x, y), (shade, shade, shade))
        star_colors = [GREEN, CYAN, YELLOW, RED, MAGENTA, (120, 160, 255), WHITE]
        for _ in range(55):
            x = rng.randrange(12, disp.rect.width - 12)
            y = rng.randrange(22, disp.rect.height - 12)
            radius = 1 if rng.random() < 0.82 else 2
            pygame.draw.circle(disp.surf, star_colors[rng.randrange(len(star_colors))],
                               (x, y), radius)
        pygame.draw.rect(disp.surf, (26, 26, 26), (0, 0, disp.rect.width, 14))
        for i, label in enumerate(("0", "5", "10", "15", "20", "25", "30", "35")):
            fit_text(disp.surf, label, [8 + i * 53, 0, 26, 13], CYAN, 9)
        ship_x = max(6, min(disp.rect.width - 8, int(state.region_x / 35 * disp.rect.width)))
        ship_y = max(18, min(disp.rect.height - 8, int(state.region_y / 20 * disp.rect.height)))
        pygame.draw.rect(disp.surf, MAGENTA, (ship_x - 6, ship_y - 6, 12, 12), 2)


def _draw_status_indicators(state):
    panel = P["Status Indicators"]
    goods = state.status_indicator_goods()
    for element in panel.elements:
        if isinstance(element, _Indicator):
            element.good = goods.pop(0) if goods else True
    pygame.draw.rect(panel.surf, BLACK, panel.lbl_distance)
    pygame.draw.rect(panel.surf, FRAME_DIM, panel.lbl_distance, 1)
    fit_text(panel.surf, f"{state.nav_distance:.1f} Ly", panel.lbl_distance, GREEN, 12)


def _draw_computer(state):
    panel = P["Computer Display"]
    options = panel.get("options")
    options.surf.fill(PANEL_BG)
    for element in panel.elements:
        if isinstance(element, Button) and element.group == "computer_menu":
            element.active = element.label == state.computer_page
    screen = panel.get("screen")
    screen.surf.fill(BLACK)
    if state.computer_page == "Self-Destruct":
        _draw_self_destruct_screen(screen, state)
        return

    fit_text(screen.surf, "TACTICAL SYSTEM DATABASE", [4, 4, screen.rect.width - 8, 16],
             WHITE, 10)
    headers = ["ID", "Rx", "Ry", "Cls", "S", "Plt"]
    classes = ["G", "M", "B", "K", "F", "A", "D", "O"]
    contact_rows = []
    for contact in state.tactical_contacts():
        cls = {"planet": "M", "ship": "K", "base": "B", "mine": "N"}.get(contact["kind"], "G")
        stat = "H" if contact.get("threat") else "N"
        contact_rows.append([
            contact["id"][:2], str(round(contact["x"])), str(round(contact["y"])),
            cls, stat, "1" if contact["kind"] == "planet" else "0",
        ])
    for block in range(4):
        x = 8 + block * 114
        for i, head in enumerate(headers):
            fit_text(screen.surf, head, [x + i * 18, 22, 17, 11], CYAN, 8)
        pygame.draw.line(screen.surf, FRAME_DIM, (x, 35), (x + 104, 35), 1)
        for row in range(15):
            system_id = block * 15 + row + 1
            y = 38 + row * 13
            if block == 0 and row < len(contact_rows):
                cells = contact_rows[row]
            else:
                cells = [
                    f"{system_id:02d}", f"{(system_id * 7) % 50}",
                    f"{(system_id * 11) % 50}", classes[system_id % len(classes)],
                    "N" if system_id % 5 else "H", str((system_id * 3) % 4),
                ]
            for i, cell in enumerate(cells):
                fg = RED if cell == "H" else GREEN
                if i == 3:
                    fg = MAGENTA if cell in ("B", "O") else YELLOW
                fit_text(screen.surf, cell, [x + i * 18, y, 17, 11], fg, 8)
    pygame.draw.rect(screen.surf, FRAME_DIM, (4, 18, screen.rect.width - 8, 222), 1)
    fit_text(screen.surf,
             f"Status: {state.alert_status}  RG {state.nav_region[0]},{state.nav_region[1]}  "
             f"Energy {state.energy_pct}%  Contacts {len(state.tactical_contacts())}",
             [8, 230, screen.rect.width - 16, 14], CYAN, 9, align="left")


def _draw_self_destruct_screen(screen, state):
    surf = screen.surf
    rect = screen.rect
    pygame.draw.rect(surf, FRAME_DIM, (4, 4, rect.width - 8, rect.height - 8), 1)
    fit_text(surf, "SELF-DESTRUCT CONTROL", [8, 10, rect.width - 16, 22],
             RED, 16, align="center")
    pygame.draw.line(surf, FRAME_DIM, (16, 42), (rect.width - 16, 42), 1)

    if state.self_destructed:
        status = "SEQUENCE COMPLETE"
        instruction = "BATTLECRUISER DESTROYED"
        status_fg = RED
    elif state.self_destruct_armed:
        status = "AUTHORIZATION ARMED"
        instruction = "SELECT SELF-DESTRUCT AGAIN TO CONFIRM"
        status_fg = YELLOW
    else:
        status = "AUTHORIZATION REQUIRED"
        instruction = "SELECT SELF-DESTRUCT TO ARM"
        status_fg = CYAN

    rows = [
        ("Status", status, status_fg),
        ("Hull", f"{state.hull_pct}%", RED if state.hull_pct < 40 else GREEN),
        ("Power", f"{state.energy_pct}%", RED if state.energy_pct < 25 else GREEN),
        ("Shields", "UP" if state.shields_up else "DOWN", GREEN if state.shields_up else RED),
        ("Velocity", f"H{state.hyper_velocity} / S{state.space_velocity}", CYAN),
        ("Alert", state.alert_status, RED if state.alert_status == "Red" else YELLOW),
    ]
    for i, (label, value, fg) in enumerate(rows):
        y = 62 + i * 22
        fit_text(surf, label + ":", [34, y, 100, 16], CYAN, 12, align="left")
        fit_text(surf, value, [142, y, 260, 16], fg, 12, align="left")

    box = pygame.Rect(36, 204, rect.width - 72, 28)
    pygame.draw.rect(surf, BLACK, box)
    pygame.draw.rect(surf, RED if state.self_destruct_armed or state.self_destructed else FRAME_DIM, box, 1)
    fit_text(surf, instruction, box.inflate(-8, 0),
             RED if state.self_destructed else (YELLOW if state.self_destruct_armed else CYAN),
             12, align="center")


def _draw_data(state):
    disp = P["Data"].get("stores")
    disp.surf.fill(BLACK)
    items = [("Torps", str(state.torpedoes)), ("Crew", str(state.crew)),
             ("Shk Troops", str(state.shock_troops)),
             ("Supplies", f"{state.supplies}t"),
             ("Probes", f"L:{state.probe_loaded} S:{state.probe_storage}"),
             ("Pods", str(state.pods)), ("Escorts", str(state.escorts))]
    for i, (label, value) in enumerate(items):
        y = 8 + i * 15
        box = pygame.Rect(disp.rect.width - 78, y, 64, 14)
        fit_text(disp.surf, label, [8, y, box.x - 16, 14], CYAN, 10, align="left")
        pygame.draw.rect(disp.surf, BLACK, box)
        pygame.draw.rect(disp.surf, FRAME_DIM, box, 1)
        fit_text(disp.surf, value, box, GREEN, 10)
    pygame.draw.rect(disp.surf, FRAME_DIM, (6, 6, disp.rect.width - 12, disp.rect.height - 12), 1)


def _draw_engineering(state):
    panel = P["Engineering Console"]
    _draw_probes(panel, state)
    _draw_damage(panel, state)
    _draw_energy(panel, state)
    _draw_velocity(panel, state)


def _draw_probes(panel, state):
    disp = panel.get("probes")
    disp.surf.fill(BLACK)
    active = next((b.label for b in panel.elements
                   if isinstance(b, Button) and b.active and b.group == "probe"), "Launch")
    if active == "Operations":
        headers = ["#", "Mode", "TG", "SS#", "R.LOC", "S.LOC", "Pw%", "Status"]
        widths = [16, 52, 44, 40, 50, 56, 36, 60]
        rows = []
        for probe in state.active_probes[:5]:
            rows.append([
                str(probe["id"]), probe["mode"], probe["target"], "039",
                f"({state.nav_region[0]},{state.nav_region[1]})",
                f"({round(probe['x'])},{round(probe['y'])})",
                str(round(probe["power"])), probe["status"],
            ])
        while len(rows) < 5:
            n = len(rows) + 1
            status = "Loaded" if n <= state.probe_loaded else ("Stored" if n <= state.probe_loaded + state.probe_storage else "Empty")
            rows.append([str(n), "Reserve", "--", "--", "--", "--", "100", status])
    else:
        headers = ["#", "Status", "TG", "RAD", "SS", "REG.L", "SYS.L", "DETECT"]
        widths = [16, 56, 36, 36, 36, 56, 60, 48]
        rows = []
        contacts = state.scanner_contacts()
        for i in range(5):
            if i < len(contacts):
                contact = contacts[i]
                rows.append([
                    str(i + 1), "Detect", contact["id"][-2:], str(round(contact["distance"])),
                    "39", f"({state.nav_region[0]},{state.nav_region[1]})",
                    f"({round(contact['x'])},{round(contact['y'])})",
                    contact["kind"].title(),
                ])
            else:
                status = "Standby" if i < state.probe_loaded else "Empty"
                rows.append([str(i + 1), status, "--", "00", "39",
                             f"({state.nav_region[0]},{state.nav_region[1]})",
                             f"({round(state.system_x)},{round(state.system_y)})", "None"])
    table(disp.surf, headers, rows, 6, 6, widths, 14, 10)


def _draw_damage(panel, state):
    disp = panel.get("velocity")  # rightmost display hosts the dynamic ship
    disp.surf.fill(BLACK)
    base_x = 6
    velocity_rail = pygame.Rect(disp.rect.width - 32, 18, 28, disp.rect.height - 36)
    img = pygame.transform.smoothscale(asset("shipdmg.png"), (130, 95))
    disp.surf.blit(img, (base_x + 4, 30))
    hull_shape = [(44, 78), (78, 54), (138, 44), (196, 62), (222, 80),
                  (196, 98), (138, 108), (78, 96)]
    pygame.draw.polygon(disp.surf, (35, 178, 45), hull_shape)
    pygame.draw.polygon(disp.surf, (12, 85, 20), hull_shape, 2)
    for y in range(56, 102, 8):
        pygame.draw.line(disp.surf, (95, 245, 95), (72, y), (202, y), 1)
    pygame.draw.rect(disp.surf, (20, 20, 20), (18, 72, 44, 16))
    pygame.draw.rect(disp.surf, FRAME_DIM, (18, 72, 44, 16), 1)
    systems_left = ["CMPTR", "S/L ENG", "HYP ENG", "SRS", "LRS", "SHD CTL"]
    systems_right = ["TRP CTL", "PHS CTL", "TELEPRT", "COM CTL", "TRAC BM", "PLS"]

    def system_color(name):
        health = state.damage.system_health.get(name, state.hull_pct)
        if health <= 0:
            return (40, 40, 40), WHITE
        if health < 40:
            return RED, WHITE
        if health < 75:
            return YELLOW, BLACK
        return GREEN, BLACK

    def system_label(rect, name, fg):
        label = font(9, True).render(name, True, color(fg))
        label_rect = label.get_rect()
        label_rect.left = rect.left + 3
        label_rect.centery = rect.centery
        disp.surf.blit(label, label_rect)

    top = 122
    row_h = 13
    row_gap = 1
    left_w = 76
    right_x = base_x + 150
    right_w = velocity_rail.x - right_x - 2
    for i, name in enumerate(systems_left):
        rect = pygame.Rect(base_x + 4, top + i * (row_h + row_gap), left_w, row_h)
        fg, text_fg = system_color(name)
        pygame.draw.rect(disp.surf, fg, rect)
        pygame.draw.rect(disp.surf, FRAME_DIM, rect, 1)
        system_label(rect, name, text_fg)
    for i, name in enumerate(systems_right):
        rect = pygame.Rect(right_x, top + i * (row_h + row_gap), right_w, row_h)
        fg, text_fg = system_color(name)
        pygame.draw.rect(disp.surf, fg, rect)
        pygame.draw.rect(disp.surf, FRAME_DIM, rect, 1)
        system_label(rect, name, text_fg)
    hull = pygame.Rect(base_x + 82, top, 66, len(systems_left) * row_h + (len(systems_left) - 1) * row_gap)
    fg, text_fg = system_color("HULL")
    pygame.draw.rect(disp.surf, fg, hull)
    pygame.draw.rect(disp.surf, FRAME_DIM, hull, 1)
    fit_text(disp.surf, f"HULL {state.hull_pct}%", hull, text_fg, 10)


def _draw_energy(panel, state):
    disp = panel.get("energy")
    disp.surf.fill(BLACK)
    rows = [("Usage", state.energy_usage, state.energy_color),
            ("Quantity", state.energy_pct, "green" if state.energy_pct >= 45 else "yellow"),
            ("Backup", state.backup_energy_pct, "green"),
            ("Shields", state.shield_pct, "yellow" if state.shields_up else "red")]
    for i, (label, pct, fg) in enumerate(rows):
        y = 10 + i * 20
        fit_text(disp.surf, label, [4, y, 60, 16], CYAN, 11, align="left")
        fit_text(disp.surf, f"{pct}%", [66, y, 36, 16], fg, 11, align="left")
        bar = pygame.Rect(106, y + 1, 268, 14)
        pygame.draw.rect(disp.surf, FRAME_DIM, bar, 1)
        fill = pygame.Rect(bar.x + 1, bar.y + 1, int((bar.width - 2) * pct / 100), bar.height - 2)
        pygame.draw.rect(disp.surf, color(fg), fill)


def _draw_velocity(panel, state):
    disp = panel.get("velocity")
    w, h = disp.size
    rail = pygame.Rect(w - 32, 18, 28, h - 36)
    pygame.draw.rect(disp.surf, BLACK, rail)
    pygame.draw.line(disp.surf, FRAME, (rail.x, rail.y), (rail.x, rail.bottom), 1)
    text_line(disp.surf, "H", (rail.x + 8, 124), MAGENTA, 9, align="center")
    text_line(disp.surf, "S", (rail.x + 21, 124), GREEN, 9, align="center")
    track_top, track_bot = 26, h - 26
    track_h = track_bot - track_top
    for bx, vel, col in [(rail.x + 8, state.hyper_velocity, MAGENTA),
                         (rail.x + 21, state.space_velocity, GREEN)]:
        pygame.draw.line(disp.surf, FRAME_DIM, (bx, track_top), (bx, track_bot), 1)
        for step in range(11):
            ty = track_bot - int(track_h * step / 10)
            pygame.draw.line(disp.surf, FRAME_DIM, (bx - 3, ty), (bx + 3, ty), 1)
        fill_h = int(track_h * vel / 10)
        pygame.draw.rect(disp.surf, col, (bx - 3, track_bot - fill_h, 6, fill_h))
        text_line(disp.surf, str(vel), (bx, track_bot + 12), col, 9, align="center")


def _draw_communication(state, current_time):
    panel = P["Communication Console"]
    left = panel.get("feed left")
    right = panel.get("feed right")
    left.surf.fill(BLACK)
    right.surf.fill(BLACK)
    mode = next((b.label for b in panel.elements
                 if isinstance(b, Button) and b.active and b.group == "comm"), "Messages")
    if mode == "Reports":
        source = [(a, b) for a, b in state.report_rows()]
    elif mode == "Combined":
        reports = state.report_rows()
        messages = state.messages
        source = [(messages[i % len(messages)][0], reports[i % len(reports)][1])
                  for i in range(max(len(messages), len(reports)))]
    else:
        source = [(a, b) for a, b in state.messages]
    if not source:
        source = [("Comms", "no traffic")]

    if current_time > state.feed_clock + 900:
        state.feed_index = (state.feed_index % len(source)) + 1
        state.feed_clock = current_time
    y = 4
    for i in range(state.feed_index):
        head, body = source[i]
        text_line(left.surf, head, (4, y), GREEN, 10)
        text_line(right.surf, body, (4, y), WHITE, 10)
        y += 14


def _draw_combat(state):
    panel = P["Combat Console"]
    _sync_combat_buttons(panel, state)
    grid = panel.get("grid")
    grid.surf.fill(BLACK)
    pygame.draw.rect(grid.surf, FRAME, grid.rect, 1)
    cx, cy = grid.rect.center
    pygame.draw.line(grid.surf, WHITE, (10, cy), (grid.rect.width - 10, cy), 2)
    pygame.draw.line(grid.surf, WHITE, (cx, 10), (cx, grid.rect.height - 10), 2)
    for step in range(-8, 9):
        gx = cx + step * 25
        gy = cy + step * 25
        if 0 < gx < grid.rect.width:
            pygame.draw.line(grid.surf, WHITE, (gx, cy - 8), (gx, cy + 8), 1)
        if 0 < gy < grid.rect.height:
            pygame.draw.line(grid.surf, WHITE, (cx - 8, gy), (cx + 8, gy), 1)

    overlay = pygame.Surface(grid.size, pygame.SRCALPHA)
    for gx in range(18, grid.rect.width, 22):
        for gy in range(18, grid.rect.height, 22):
            dot = (95, 120, 235, 100) if abs(gx - cx) + abs(gy - cy) > 130 else (210, 120, 55, 120)
            pygame.draw.circle(overlay, dot, (gx, gy), 2)
    pygame.draw.circle(overlay, (90, 110, 230, 150), (cx, cy), 165, 2)
    pygame.draw.circle(overlay, (255, 140, 80, 150), (cx, cy), 105, 2)
    grid.surf.blit(overlay, (0, 0))
    for deg in range(0, 360, 15):
        if deg % 30 == 0:
            rad = math.radians(deg - 90)
            tx = cx + int(178 * math.cos(rad))
            ty = cy + int(178 * math.sin(rad))
            text_line(grid.surf, str(deg), (tx, ty), WHITE, 10, align="center")
    for contact in state.tactical_contacts():
        dx = contact["x"] - state.system_x
        dy = contact["y"] - state.system_y
        if state.combat_alignment == "BCS":
            angle = math.radians(-state.actual_heading)
            dx, dy = (dx * math.cos(angle) - dy * math.sin(angle),
                      dx * math.sin(angle) + dy * math.cos(angle))
        px = max(18, min(grid.rect.width - 18, cx + int(dx * 15)))
        py = max(18, min(grid.rect.height - 18, cy + int(dy * 15)))
        selected = contact["id"] == state.selected_target["id"]
        col = RED if contact.get("threat") else (GREEN if contact["kind"] == "base" else CYAN)
        shape = [(px, py - 9), (px + 9, py + 7), (px - 9, py + 7)]
        if contact["kind"] == "mine":
            pygame.draw.circle(grid.surf, RED, (px, py), 6, 2)
        else:
            pygame.draw.polygon(grid.surf, col, shape)
        if selected:
            pygame.draw.rect(grid.surf, MAGENTA, (px - 12, py - 12, 24, 24), 1)

    grid.surf.blit(pygame.transform.smoothscale(asset("combcShip.png"), (34, 34)),
                   (cx - 17, cy - 17))

    _draw_weapons(panel, state)
    _draw_shields(panel, state)
    _draw_fire_controls(panel, state)
    _draw_target_data(panel, state)


def _sync_combat_buttons(panel, state):
    active_by_group = {
        "combat_align": state.combat_alignment,
        "combat_weapon": state.selected_weapon,
        "shield": state.shield_policy,
        "weapon_condition": "Cont" if state.weapon_condition == "Cont"
        else {"Phaser": "Ph", "Trp1": "T1", "Trp2": "T2"}.get(state.selected_weapon, "Ph"),
    }
    for element in panel.elements:
        if isinstance(element, Button):
            if element.group in active_by_group:
                element.active = element.label == active_by_group[element.group]
            elif element.label == "ECM":
                element.active = state.ecm_enabled


def _draw_weapons(panel, state):
    box = pygame.Rect(485, 35, 165, 130)
    pygame.draw.rect(panel.surf, PANEL_BG, box)
    pygame.draw.rect(panel.surf, GREY, box, 2)
    fit_text(panel.surf, "Weapons", [box.x + 4, box.y + 2, 100, 14], CYAN, 11, align="left")
    for i in range(4):
        ready = state.weapon_reload[i] <= 0
        cell = pygame.Rect(box.x + 6 + i * 39, box.y + 20, 37, 18)
        pygame.draw.rect(panel.surf, GREEN if ready else RED, cell)
        pygame.draw.rect(panel.surf, BLACK, cell, 1)
    fit_text(panel.surf, "Qty:", [box.x + 88, box.y + 43, 26, 14], BLACK, 10, align="right")
    qty = pygame.Rect(box.x + 118, box.y + 42, 36, 16)
    pygame.draw.rect(panel.surf, BLACK, qty)
    pygame.draw.rect(panel.surf, WHITE, qty, 2)
    fit_text(panel.surf, str(state.torpedoes), qty.inflate(-3, -2), GREEN, 10)

    mode_box = pygame.Rect(box.x + 8, box.y + 58, 46, 18)
    setting_box = pygame.Rect(box.x + 8, box.y + 90, 56, 18)
    pygame.draw.rect(panel.surf, CYAN, mode_box)
    pygame.draw.rect(panel.surf, CYAN, setting_box)
    fit_text(panel.surf, "Mode", mode_box, BLACK, 10)
    fit_text(panel.surf, "Setting", setting_box, BLACK, 10)
    fit_text(panel.surf, "Auto", [box.x + 18, box.y + 78, 42, 12],
             RED if state.weapon_auto else BLACK, 9, align="left")
    fit_text(panel.surf, "Manual", [box.x + 76, box.y + 78, 50, 12],
             RED if not state.weapon_auto else BLACK, 9, align="left")
    settings = [("Destroy", 98), ("Disable", 98), ("Standby", 112), ("Conditional", 112)]
    for i, (label, y) in enumerate(settings):
        x = box.x + 18 if i % 2 == 0 else box.x + 76
        hot = RED if state.weapon_setting == label else BLACK
        fit_text(panel.surf, label, [x, box.y + y, 66, 12], hot, 8, align="left")

    ready_text = "READY" if state.weapon_reload[state.weapon_index] <= 0 else f"{state.weapon_reload[state.weapon_index]:.1f}s"
    fit_text(panel.surf, ready_text, [box.x + 8, box.y + 42, 72, 14],
             GREEN if ready_text == "READY" else YELLOW, 8, align="left")


def _draw_shields(panel, state):
    box = pygame.Rect(485, 172, 165, 170)
    pygame.draw.rect(panel.surf, PANEL_BG, box)
    pygame.draw.rect(panel.surf, GREY, box, 2)
    fit_text(panel.surf, "Shields", [box.x + 4, box.y + 2, 80, 14], CYAN, 11, align="left")
    center = (box.centerx, box.y + 70)
    arcs = [(225, 315), (135, 225), (45, 135), (315, 45)]
    for idx, (start, end) in enumerate(arcs):
        strength = state.shield_strength[idx] if state.shields_up else 0
        col = GREEN if strength >= 500 else (YELLOW if strength > 0 else RED)
        label = f"{idx + 1}:{strength}"
        _arc_quadrant(panel.surf, center, 38, 56, start, end, col)
        mid = math.radians((start + (end if end > start else end + 360)) / 2)
        lx = center[0] + int(47 * math.cos(mid))
        ly = center[1] + int(47 * math.sin(mid))
        text_line(panel.surf, label, (lx, ly), BLACK, 9, align="center")
    panel.surf.blit(pygame.transform.smoothscale(asset("babaaa 2.png"), (28, 40)),
                    (center[0] - 14, center[1] - 20))
    text_line(panel.surf, "Shield Mode", (box.x + 6, box.y + 118), CYAN, 10)
    fit_text(panel.surf, state.shield_policy, [box.x + 70, box.y + 111, 80, 14],
             GREEN if state.shields_up else RED, 10, align="left")
    fit_text(panel.surf, f"AAS: {'Y' if state.aas_enabled else 'N'}",
             [box.x + 6, box.y + 132, 70, 13], CYAN, 9, align="left")


def _draw_fire_controls(panel, state):
    box = pygame.Rect(485, 346, 165, 46)
    pygame.draw.rect(panel.surf, PANEL_BG, box)
    pygame.draw.rect(panel.surf, GREY, box, 2)
    for i, label in enumerate(("Ph", "T1", "T2", "Cont")):
        cell = pygame.Rect(box.x + 8 + i * 39, box.y + 7, 37, 30)
        pygame.draw.rect(panel.surf, GREEN if label != "Cont" else CYAN, cell)
        pygame.draw.rect(panel.surf, BLACK, cell, 1)
        manual = "Manual" if label != "Cont" else ""
        fit_text(panel.surf, manual, [cell.x, cell.y + 19, cell.w, 9], BLACK, 7)
    fit_text(panel.surf, state.weapon_condition, [box.x + 8, box.y + 36, 146, 9],
             GREEN, 8, align="right")


def _draw_target_data(panel, state):
    box = pygame.Rect(485, 396, 165, 100)
    pygame.draw.rect(panel.surf, BLACK, box)
    pygame.draw.rect(panel.surf, GREY, box, 2)
    fit_text(panel.surf, "Target Data", [box.x + 6, box.y + 4, 86, 15], CYAN, 10, align="left")
    solution = state.target_solution()
    headers = ["R.Pos", "Brng", "Vel", "Wpn"]
    values = [solution["rpos"], solution["bearing"], solution["velocity"], solution["weapon"][:4]]
    widths = [50, 43, 34, 34]
    x = box.x + 4
    y = box.y + 28
    for i, header in enumerate(headers):
        pygame.draw.line(panel.surf, FRAME_DIM, (x, y), (x, box.bottom - 3), 1)
        fit_text(panel.surf, header, [x + 2, y, widths[i] - 4, 14], CYAN, 9)
        fit_text(panel.surf, values[i], [x + 2, y + 22, widths[i] - 4, 16],
                 RED if header == "Wpn" else GREEN, 10)
        x += widths[i]
    pygame.draw.line(panel.surf, FRAME_DIM, (x, y), (x, box.bottom - 3), 1)
    target_name = state.selected_target["name"][:17]
    fit_text(panel.surf, target_name, [box.x + 6, box.y + 78, box.w - 12, 14],
             YELLOW if state.selected_target.get("threat") else GREEN, 9, align="left")
    fit_text(panel.surf,
             f"H:{solution['hull']} S:{solution['shields']} {solution['status'][:8]}",
             [box.x + 6, box.y + 62, box.w - 12, 13],
             RED if solution["hull"] <= 35 else CYAN, 8, align="left")


def _arc_quadrant(surface, center, r_in, r_out, start, end, col):
    if end <= start:
        end += 360
    pts_out = [(center[0] + r_out * math.cos(math.radians(a)),
                center[1] + r_out * math.sin(math.radians(a)))
               for a in range(start, end + 1, 4)]
    pts_in = [(center[0] + r_in * math.cos(math.radians(a)),
               center[1] + r_in * math.sin(math.radians(a)))
              for a in range(end, start - 1, -4)]
    poly = pts_out + pts_in
    if len(poly) >= 3:
        pygame.draw.polygon(surface, col, poly)
        pygame.draw.polygon(surface, BLACK, poly, 1)


def _draw_strategic(state):
    panel = P["Strategic Command Console"]
    escort_rows = [["BC", "CMD", "FLAG"]]
    for idx in range(max(0, state.escorts)):
        order = "ESCORT" if idx < 2 else "HOLD"
        escort_rows.append([f"D{idx + 1}", "DD", order])
    table(panel.get("escort").surf, ["ID", "TYPE", "ORD"], escort_rows[:7],
          5, 6, [30, 44, 70], 15, 10)
    form = panel.get("formation")
    form.surf.fill(BLACK)
    pygame.draw.circle(form.surf, GREEN, (40, 30), 5)
    pygame.draw.circle(form.surf, GREEN, (20, 74), 4)
    pygame.draw.circle(form.surf, YELLOW, (60, 74), 4)
    pygame.draw.line(form.surf, CYAN, (40, 34), (20, 74), 1)
    pygame.draw.line(form.surf, CYAN, (40, 34), (60, 74), 1)
    text_rows(form.surf, [("DELTA", "cyan"), (f"{state.nav_distance:.1f} LY", "green"),
                          (state.alert_status.upper(), "yellow")],
              16, 90, 12, 9)
    fleet_rows = [["KLG-1", "0.0", state.alert_status.upper()]]
    for idx in range(max(0, state.escorts)):
        rng = f"{1.2 + idx * 0.6:.1f}"
        stat = "READY" if idx < 2 else "HOLD"
        fleet_rows.append([f"DES-{idx + 1}", rng, stat])
    table(panel.get("fleet pos").surf, ["SHIP", "RNG", "STAT"], fleet_rows[:6],
          6, 6, [48, 42, 66], 15, 10)
    fleet = panel.get("fleet cmd")
    fleet.surf.fill(BLACK)
    groups = [
        ("Battle Fleets", ["Hotspur", "Panzer", state.selected_target["name"], "Rifle", "Sickle"]),
        ("Supply Fleets", ["Liberation", "Graviton", f"{state.supplies}t stores", "Cosmic Lance"]),
        ("Legion Fleets", ["Leviathan", "Sunblock", f"{state.shock_troops} troops", "Paramount"]),
    ]
    y = 8
    for title, names in groups:
        fit_text(fleet.surf, title, [8, y, 110, 12], MAGENTA, 9, align="left")
        y += 14
        for col, name in enumerate(names):
            x = 8 + col * 138
            fit_text(fleet.surf, f"{col + 1}", [x, y, 14, 12], CYAN, 9)
            fit_text(fleet.surf, f"KS-{col + 1}", [x + 18, y, 40, 12], WHITE, 9, align="left")
            fit_text(fleet.surf, name, [x + 58, y, 72, 12], WHITE, 9, align="left")
        y += 28
        pygame.draw.line(fleet.surf, FRAME_DIM, (4, y - 8), (fleet.rect.width - 4, y - 8), 1)


def _draw_log(state):
    disp = P["Commanders Log"].get("log")
    text_rows(disp.surf, [
        ("IMPERIAL TRIBUNE", "cyan"), ("STARDATE 7421.6", "green"),
        ("Klagar-class", "green"),
        (f"battlecruiser {state.nav_mode.lower()}", "green"),
        (f"near {state.selected_target['name'][:18]}.", "green"),
        (f"Stores: {state.torpedoes} torpedoes,", "green"),
        (f"{round(state.energy_units)} power units,", "green"),
        (f"{state.supplies} tons supplies.", "green"),
        (f"{state.shock_troops} shock troops ready.", "yellow"), ("", "green"),
        ("Standing order:", "cyan"), ("complete training", "cyan"),
        ("patrol and report.", "cyan"),
    ], 8, 8, 18, 11)
