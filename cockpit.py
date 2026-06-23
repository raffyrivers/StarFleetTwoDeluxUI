"""Builds every console panel and draws its per-frame content.

Layout coordinates match the Star Fleet II Deluxe command screen. Static
readouts are expressed as data and rendered through shared helpers so text
always fits its box and the code stays compact.
"""

import math
import pygame
import core
from core import (BLACK, PANEL_BG, FRAME, FRAME_DIM, CYAN, GREEN, RED, YELLOW,
                  GREY, MAGENTA, WHITE, color, font, fit_text, text_line, asset)
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


def table(surface, headers, rows, x, y, widths, line_h=14, size=10):
    cx = x
    for i, head in enumerate(headers):
        fit_text(surface, head, [cx, y, widths[i] - 2, line_h], CYAN, size, align="left")
        cx += widths[i]
    pygame.draw.line(surface, FRAME, (x, y + line_h), (x + sum(widths), y + line_h), 1)
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
        (10, 30, 440, 330, "Navigation Console", 168),
        (455, 30, 192, 225, "Science Console", 130),
        (656, 50, 655, 385, "Primary Display", 130),
        (1330, 30, 440, 60, "Status Indicators", 140),
        (451, 265, 197, 170, "Navigation", 0),
        (10, 361, 440, 225, "Star Map", 0),
        (1330, 110, 580, 260, "Computer Display", 140),
        (490, 455, 160, 135, "Data", 60),
        (660, 455, 655, 550, "Combat Console", 130),
        (1330, 390, 580, 350, "Strategic Command Console", 200),
        (10, 605, 640, 240, "Engineering Console", 160),
        (10, 865, 640, 205, "Communication Console", 180),
        (1330, 760, 330, 310, "Security Console", 130),
        (1670, 760, 240, 310, "Commanders Log", 150),
    ]
    for x, y, w, h, label, tab in layout:
        P[label] = Panel(x, y, w, h, label, tab)

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
    video = VideoDisplay(panel, "primary", (645, 320), (5, 5))
    video.set_videos(["DeepSpace.mp4", "EarthOrbit.mp4"])
    Text(panel, (5, 350), "Msn Elapsed", "cyan", 11)
    panel.lbl_elapsed = pygame.Rect(95, 344, 84, 18)
    Text(panel, (190, 350), "Time Left", "cyan", 11)
    panel.lbl_left = pygame.Rect(255, 344, 84, 18)
    Button(panel, (360, 333, 64, 18), "REST", text_size=11)
    Button(panel, (360, 356, 64, 18), "Sim Freeze", text_size=11)


def _build_science():
    panel = P["Science Console"]
    CircleDisplay(panel, "scope", (5, 24), 90)
    Text(panel, (4, 6), "LRS", "cyan", 12)
    Button(panel, (150, 4, 36, 16), "SRS", text_size=11)
    Button(panel, (4, 205, 78, 16), "Dept Q", text_size=11)
    Button(panel, (110, 205, 78, 16), "Planet Data", text_size=11)


def _build_navigation():
    panel = P["Navigation Console"]
    Display(panel, "orbit", (210, 210), (5, 24))
    Display(panel, "system", (210, 210), (225, 24))
    Text(panel, (5, 8), "Orbital Displays", "cyan", 11)
    Text(panel, (228, 8), "System Map", "cyan", 11)
    nav = VideoDisplay(panel, "nav video", (430, 70), (5, 256))
    nav.set_videos(["mmn.mp4"])
    Button(panel, (5, 238, 64, 16), "Objects", key=pygame.K_i, group="nav", text_size=11)
    Button(panel, (72, 238, 82, 16), "Orbit Zones", key=pygame.K_o, group="nav", text_size=11)
    Button(panel, (157, 238, 96, 16), "Mercator Map", key=pygame.K_p, group="nav", text_size=11)


def _build_navigation_data():
    panel = P["Navigation"]
    Display(panel, "nav grid", (192, 145), (2, 22), double_border=False)


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
    Display(panel, "options", (90, 250), (5, 5))
    Display(panel, "screen", (475, 250), (100, 5))


def _build_data():
    panel = P["Data"]
    Display(panel, "stores", (150, 120), (5, 10))


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
    Button(panel, (485, 488, 60, 16), "Board", key=pygame.K_RSHIFT, text_size=10)


def _build_strategic():
    panel = P["Strategic Command Console"]
    Display(panel, "escort", (150, 120), (5, 12))
    Display(panel, "formation", (80, 120), (165, 12))
    Display(panel, "fleet pos", (200, 120), (255, 12))
    Display(panel, "fleet cmd", (570, 195), (5, 150))
    Button(panel, (455, 10, 120, 17), "Escort Commands", text_size=12)
    Button(panel, (455, 40, 120, 17), "Fleet Commands", text_size=12)
    Button(panel, (455, 70, 120, 17), "Strategic Commands", text_size=12)
    Button(panel, (455, 100, 120, 17), "Menu", text_size=12)
    Button(panel, (455, 128, 58, 17), "Editor", text_size=12)
    Button(panel, (517, 128, 58, 17), "View", text_size=12)


def _build_security():
    panel = P["Security Console"]
    Display(panel, "internal", (320, 160), (5, 18))
    Display(panel, "prisoners", (130, 100), (5, 205))
    Display(panel, "interrogations", (165, 100), (160, 205))
    Text(panel, (5, 190), "Prisoner Status", "cyan", 12)


def _build_log():
    panel = P["Commanders Log"]
    Display(panel, "log", (228, 298), (5, 6))


# --- per-frame drawing ------------------------------------------------------

def draw(state, current_time):
    _draw_primary(state)
    _draw_science()
    _draw_navigation()
    _draw_navigation_data()
    _draw_star_map()
    _draw_status_indicators()
    _draw_computer()
    _draw_data()
    _draw_engineering(state)
    _draw_communication(state, current_time)
    _draw_combat(state)
    _draw_strategic()
    _draw_security()
    _draw_log()


def _draw_primary(state):
    panel = P["Primary Display"]
    pygame.draw.rect(panel.surf, BLACK, panel.lbl_elapsed)
    pygame.draw.rect(panel.surf, FRAME_DIM, panel.lbl_elapsed, 1)
    fit_text(panel.surf, "15.24 Days", panel.lbl_elapsed, GREEN, 13)
    pygame.draw.rect(panel.surf, BLACK, panel.lbl_left)
    pygame.draw.rect(panel.surf, FRAME_DIM, panel.lbl_left, 1)
    fit_text(panel.surf, "5.26 Days", panel.lbl_left, GREEN, 13)
    status = pygame.Rect(540, 333, 100, 40)
    pygame.draw.rect(panel.surf, GREEN, status)
    fit_text(panel.surf, "Status: Green", status, BLACK, 13)


def _draw_science():
    scope = P["Science Console"].get("scope")
    cx, cy = scope.rect.center
    pygame.draw.line(scope.surf, WHITE, (cx, 0), (cx, scope.rect.height), 1)
    pygame.draw.line(scope.surf, WHITE, (0, cy), (scope.rect.width, cy), 1)
    for i in range(0, scope.rect.width, 15):
        pygame.draw.line(scope.surf, FRAME_DIM, (cx - 8, i), (cx + 8, i), 1)
        pygame.draw.line(scope.surf, FRAME_DIM, (i, cy - 8), (i, cy + 8), 1)
    pygame.draw.circle(scope.surf, GREEN, (cx + 28, cy - 34), 3)
    pygame.draw.circle(scope.surf, RED, (cx - 40, cy + 22), 3)
    pygame.draw.circle(scope.surf, YELLOW, scope.rect.center, 4)


def _draw_navigation():
    panel = P["Navigation Console"]
    orbit = panel.get("orbit")
    system = panel.get("system")
    for disp in (orbit, system):
        grid = pygame.Surface(disp.size, pygame.SRCALPHA)
        for gx in range(0, disp.rect.width, 21):
            pygame.draw.line(grid, (255, 255, 255, 40), (gx, 0), (gx, disp.rect.height))
        for gy in range(0, disp.rect.height, 21):
            pygame.draw.line(grid, (255, 255, 255, 40), (0, gy), (disp.rect.width, gy))
        disp.surf.blit(grid, (0, 0))
    cx, cy = system.rect.center
    pygame.draw.circle(system.surf, RED, (cx, cy), 90, 1)
    pygame.draw.circle(system.surf, (60, 120, 220), (cx, cy), 55, 1)
    pygame.draw.circle(system.surf, YELLOW, (cx, cy), 8)
    pygame.draw.circle(system.surf, (255, 150, 60), (cx + 70, cy - 30), 5)
    pygame.draw.circle(system.surf, CYAN, (cx - 38, cy + 36), 4)
    for label, dx, dy in [("N", cx, 10), ("S", cx, disp.rect.height - 10),
                          ("E", disp.rect.width - 12, cy), ("W", 12, cy)]:
        text_line(orbit.surf, label, (dx, dy), CYAN, 10, align="center")


def _draw_navigation_data():
    grid = P["Navigation"].get("nav grid")
    grid.surf.fill(BLACK)
    rows = [
        ("Reg Loc:", "4, 6", GREEN), ("Orb Pos:", "40 / 0", GREEN),
        ("Dist Trgt:", "1.4", GREEN), ("Course:", "135", GREEN),
        ("Target:", "40, 0", GREEN), ("Object:", "Planet", GREEN),
        ("Mode:", "Hyperspace", CYAN),
    ]
    readout(grid.surf, rows, 6, 6, 19, 11, 78)
    pygame.draw.rect(grid.surf, FRAME_DIM, (6, 6, grid.rect.width - 12, grid.rect.height - 12), 1)


def _draw_star_map():
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
        grid = pygame.Surface(disp.size, pygame.SRCALPHA)
        for gx in range(0, disp.rect.width, 24):
            pygame.draw.line(grid, (50, 80, 200, 60), (gx, 0), (gx, disp.rect.height))
        for gy in range(0, disp.rect.height, 24):
            pygame.draw.line(grid, (50, 80, 200, 60), (0, gy), (disp.rect.width, gy))
        disp.surf.blit(grid, (0, 0))
        text_line(disp.surf, "MERCATOR MAP", (8, 6), CYAN, 11)


def _draw_status_indicators():
    panel = P["Status Indicators"]
    pygame.draw.rect(panel.surf, BLACK, panel.lbl_distance)
    pygame.draw.rect(panel.surf, FRAME_DIM, panel.lbl_distance, 1)
    fit_text(panel.surf, "4.8 Ly", panel.lbl_distance, GREEN, 12)


def _draw_computer():
    panel = P["Computer Display"]
    options = panel.get("options")
    options.surf.fill(BLACK)
    text_rows(options.surf, [
        ("SHIP", "red"), ("NAV", "green"), ("SCI", "green"), ("TACT", "green"),
        ("CREW", "green"), ("LOG", "green"), ("ALERT", "yellow"),
    ], 8, 12, 24, 11)
    screen = panel.get("screen")
    screen.surf.fill(BLACK)
    text_rows(screen.surf, [("COMPUTER QUERY: MISSION STATUS", "cyan"),
                            ("-" * 32, "cyan")], 10, 8, 14, 11)
    readout(screen.surf, [
        ("Stardate", "7421.6", GREEN), ("Base", "Starfort SF-1", GREEN),
        ("Ship", "Klagar-class BC", GREEN), ("Mission", "training patrol", GREEN),
        ("Torps", "24 loaded", GREEN), ("Power", "4000 units", GREEN),
        ("Supplies", "1000 tons", GREEN), ("Exec", "briefing active", YELLOW),
    ], 12, 44, 21, 12, 70)
    table(screen.surf, ["SYS", "STATE", "CAP", "NOTE"], [
        ["NAV", "DOCK", "100", "SF-1"], ["ENG", "READY", "4000", "power"],
        ["CMB", "ARM", "24", "torps"], ["TRP", "READY", "100", "beam"],
    ], 282, 46, [36, 50, 40, 78], 18, 11)


def _draw_data():
    disp = P["Data"].get("stores")
    disp.surf.fill(BLACK)
    items = [("Torps", "24"), ("Crew", "275"), ("Shk Troops", "150"),
             ("Supplies", "1000t"), ("Probes", "L:5 S:5"), ("Pods", "2"),
             ("Escorts", "4")]
    for i, (label, value) in enumerate(items):
        y = 14 + i * 15
        box = pygame.Rect(96, y, 50, 13)
        fit_text(disp.surf, label, [8, y, 84, 13], CYAN, 10, align="left")
        pygame.draw.rect(disp.surf, BLACK, box)
        pygame.draw.rect(disp.surf, FRAME_DIM, box, 1)
        fit_text(disp.surf, value, box, GREEN, 10)


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
        rows = [
            ["1", "Survey", "SS42", "043", "(4,6)", "(49,43)", "92", "Mapping"],
            ["2", "Relay", "SS35", "030", "(3,8)", "(51,67)", "81", "Linked"],
            ["3", "Scout", "SS10", "009", "(2,9)", "(52,24)", "64", "Silent"],
            ["4", "Track", "SS45", "041", "(0,8)", "(21,63)", "77", "Contact"],
            ["5", "Reserve", "SS36", "007", "(0,4)", "(21,63)", "100", "Docked"],
        ]
    else:
        headers = ["#", "Status", "TG", "RAD", "SS", "REG.L", "SYS.L", "DETECT"]
        widths = [16, 56, 36, 36, 36, 56, 60, 48]
        rows = [
            ["1", "Survey", "43", "12", "39", "(6,7)", "(49,43)", "Bio"],
            ["2", "Relay", "30", "08", "35", "(2,8)", "(51,67)", "Com"],
            ["3", "Scout", "09", "03", "10", "(2,9)", "(52,24)", "Ore"],
            ["4", "Track", "41", "16", "45", "(0,8)", "(21,63)", "Ship"],
            ["5", "Standby", "07", "00", "36", "(0,4)", "(21,63)", "None"],
        ]
    table(disp.surf, headers, rows, 6, 6, widths, 14, 10)


def _draw_damage(panel, state):
    disp = panel.get("velocity")  # rightmost display hosts the dynamic ship
    # Damage detail is drawn directly on the panel beside the velocity column.
    base_x = 386
    img = pygame.transform.smoothscale(asset("shipdmg.png"), (130, 95))
    panel.surf.blit(img, (base_x + 4, 30))
    systems_left = ["CMPTR", "S/L ENG", "HYP ENG", "SRS", "LRS", "SHD CTL"]
    systems_right = ["TRP CTL", "PHS CTL", "TELEPRT", "COM CTL", "TRAC BM", "PLS"]
    palette = {1: GREEN, 2: YELLOW, 3: RED, 4: (40, 40, 40)}
    fg = palette[state.damage_level]
    text_fg = BLACK if state.damage_level in (1,) else "white"
    top = 138
    for i, name in enumerate(systems_left):
        rect = pygame.Rect(base_x + 4, top + i * 13, 70, 12)
        pygame.draw.rect(panel.surf, fg, rect)
        pygame.draw.rect(panel.surf, FRAME_DIM, rect, 1)
        fit_text(panel.surf, name, rect, text_fg, 9, align="left")
    for i, name in enumerate(systems_right):
        rect = pygame.Rect(base_x + 160, top + i * 13, 70, 12)
        pygame.draw.rect(panel.surf, fg, rect)
        pygame.draw.rect(panel.surf, FRAME_DIM, rect, 1)
        fit_text(panel.surf, name, rect, text_fg, 9, align="left")
    hull = pygame.Rect(base_x + 78, top, 78, 77)
    pygame.draw.rect(panel.surf, fg, hull)
    pygame.draw.rect(panel.surf, FRAME_DIM, hull, 1)
    fit_text(panel.surf, "HULL", hull, text_fg, 12)


def _draw_energy(panel, state):
    disp = panel.get("energy")
    disp.surf.fill(BLACK)
    rows = [("Usage", state.energy_usage, state.energy_color),
            ("Quantity", 94, "green"), ("Backup", 100, "green"),
            ("Shields", 58, "yellow")]
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
    disp.surf.fill(BLACK)
    w, h = disp.size
    mid = w // 2
    pygame.draw.line(disp.surf, FRAME, (mid, 10), (mid, h - 10), 1)
    text_line(disp.surf, "HYP", (mid - 40, 6), MAGENTA, 11, align="center")
    text_line(disp.surf, "SPC", (mid + 40, 6), GREEN, 11, align="center")
    track_top, track_bot = 26, h - 26
    track_h = track_bot - track_top
    for x_off, vel, col in [(-22, state.hyper_velocity, MAGENTA),
                            (22, state.space_velocity, GREEN)]:
        bx = mid + x_off
        pygame.draw.line(disp.surf, FRAME_DIM, (bx, track_top), (bx, track_bot), 1)
        for step in range(11):
            ty = track_bot - int(track_h * step / 10)
            pygame.draw.line(disp.surf, FRAME_DIM, (bx - 5, ty), (bx + 5, ty), 1)
        fill_h = int(track_h * vel / 10)
        pygame.draw.rect(disp.surf, col, (bx - 4, track_bot - fill_h, 8, fill_h))
        text_line(disp.surf, str(vel), (bx, track_bot + 12), col, 11, align="center")


def _draw_communication(state, current_time):
    panel = P["Communication Console"]
    left = panel.get("feed left")
    right = panel.get("feed right")
    left.surf.fill(BLACK)
    right.surf.fill(BLACK)
    mode = next((b.label for b in panel.elements
                 if isinstance(b, Button) and b.active and b.group == "comm"), "Messages")
    if mode == "Reports":
        source = [(a, b) for a, b in REPORTS]
    elif mode == "Combined":
        source = [(MESSAGES[i][0], REPORTS[i][1]) for i in range(len(MESSAGES))]
    else:
        source = [(a, b) for a, b in MESSAGES]

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

    grid_btn = next((b for b in panel.elements
                     if isinstance(b, Button) and b.label == "Grid"), None)
    if grid_btn and grid_btn.active:
        overlay = pygame.Surface(grid.size, pygame.SRCALPHA)
        for gx in range(15, grid.rect.width, 25):
            for gy in range(15, grid.rect.height, 25):
                pygame.draw.circle(overlay, (90, 110, 230, 90), (gx, gy), 2)
        pygame.draw.circle(overlay, (90, 110, 230, 120), (cx, cy), 165, 2)
        pygame.draw.circle(overlay, (255, 140, 80, 120), (cx, cy), 105, 2)
        grid.surf.blit(overlay, (0, 0))

    head_btn = next((b for b in panel.elements
                     if isinstance(b, Button) and b.label == "Head"), None)
    if head_btn and head_btn.active:
        for deg in range(0, 360, 30):
            rad = math.radians(deg - 90)
            tx = cx + int(150 * math.cos(rad))
            ty = cy + int(150 * math.sin(rad))
            text_line(grid.surf, str(deg), (tx, ty), WHITE, 10, align="center")

    grid.surf.blit(pygame.transform.smoothscale(asset("combcShip.png"), (34, 34)),
                   (cx - 17, cy - 17))

    _draw_weapons(panel, state)
    _draw_shields(panel, state)


def _draw_weapons(panel, state):
    box = pygame.Rect(485, 35, 165, 130)
    pygame.draw.rect(panel.surf, PANEL_BG, box)
    pygame.draw.rect(panel.surf, GREY, box, 2)
    fit_text(panel.surf, "Weapons", [box.x + 4, box.y + 2, 100, 14], CYAN, 11, align="left")
    for i, name in enumerate(state.weapons):
        cell = pygame.Rect(box.x + 6 + i * 39, box.y + 20, 37, 16)
        active = i == state.weapon_index
        pygame.draw.rect(panel.surf, GREEN if active else (30, 30, 30), cell)
        pygame.draw.rect(panel.surf, BLACK, cell, 1)
        fit_text(panel.surf, name, cell, BLACK if active else WHITE, 10)
    labels = [("Mode", "Auto / Manual"), ("Set", "Destroy / Disable")]
    for i, (tag, val) in enumerate(labels):
        y = box.y + 44 + i * 22
        tag_box = pygame.Rect(box.x + 6, y, 44, 16)
        pygame.draw.rect(panel.surf, CYAN, tag_box)
        fit_text(panel.surf, tag, tag_box, BLACK, 10)
        fit_text(panel.surf, val, [box.x + 56, y, 104, 16], GREY, 10, align="left")
    info = pygame.Rect(box.x + 6, box.y + 92, 153, 30)
    fit_text(panel.surf, "Bmb: N   Qty: 24   ECM: Y", info, GREEN, 10, align="left")


def _draw_shields(panel, state):
    box = pygame.Rect(485, 172, 165, 170)
    pygame.draw.rect(panel.surf, PANEL_BG, box)
    pygame.draw.rect(panel.surf, GREY, box, 2)
    fit_text(panel.surf, "Shields", [box.x + 4, box.y + 2, 80, 14], CYAN, 11, align="left")
    center = (box.centerx, box.y + 70)
    quad = [(225, 315, GREEN, "1:500"), (315, 45, RED, "4:0"),
            (45, 135, GREEN, "3:1000"), (135, 225, GREEN, "2:2000")]
    for start, end, col, label in quad:
        _arc_quadrant(panel.surf, center, 38, 56, start, end, col)
        mid = math.radians((start + (end if end > start else end + 360)) / 2)
        lx = center[0] + int(47 * math.cos(mid))
        ly = center[1] + int(47 * math.sin(mid))
        text_line(panel.surf, label, (lx, ly), BLACK, 9, align="center")
    panel.surf.blit(pygame.transform.smoothscale(asset("babaaa 2.png"), (28, 40)),
                    (center[0] - 14, center[1] - 20))
    text_line(panel.surf, "Shield Mode", (box.x + 6, box.y + 118), CYAN, 10)


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


def _draw_strategic():
    panel = P["Strategic Command Console"]
    table(panel.get("escort").surf, ["ID", "TYPE", "ORD"], [
        ["BC", "CMD", "FLAG"], ["D1", "DD", "ESCORT"],
        ["D2", "DD", "ESCORT"], ["D3", "DD", "HOLD"],
    ], 5, 6, [30, 44, 70], 15, 10)
    form = panel.get("formation")
    pygame.draw.circle(form.surf, GREEN, (40, 30), 5)
    pygame.draw.circle(form.surf, GREEN, (20, 74), 4)
    pygame.draw.circle(form.surf, YELLOW, (60, 74), 4)
    pygame.draw.line(form.surf, CYAN, (40, 34), (20, 74), 1)
    pygame.draw.line(form.surf, CYAN, (40, 34), (60, 74), 1)
    text_rows(form.surf, [("DELTA", "cyan"), ("4.8 LY", "green"), ("AFT ARC", "yellow")],
              16, 90, 12, 9)
    table(panel.get("fleet pos").surf, ["SHIP", "RNG", "STAT"], [
        ["KLG-1", "0.0", "READY"], ["DES-1", "1.2", "READY"],
        ["DES-2", "1.8", "READY"], ["DES-3", "2.4", "HOLD"],
    ], 6, 6, [48, 42, 66], 15, 10)
    table(panel.get("fleet cmd").surf, ["ORDER", "TARGET", "TIME", "STATUS"], [
        ["SCREEN", "BC FLAG", "00:18", "ACTIVE"], ["DOCK", "SF-1", "00:42", "HOLD"],
        ["ESCORT", "CONVOY", "01:10", "QUEUED"], ["SURVEY", "REG 6,0", "02:30", "ACTIVE"],
        ["RECALL", "PROBE 3", "03:05", "QUEUED"],
    ], 8, 8, [86, 96, 60, 80], 17, 11)


def _draw_security():
    panel = P["Security Console"]
    table(panel.get("internal").surf, ["DECK", "AREA", "STATE", "TEAM"], [
        ["02", "BRIDGE", "CLEAR", "A"], ["05", "ARMORY", "LOCK", "B"],
        ["07", "CARGO", "CAUTION", "C"], ["09", "MED BAY", "CLEAR", "D"],
        ["12", "SHUTTLE", "CLEAR", "E"], ["15", "BRIG", "LOCK", "F"],
    ], 6, 8, [38, 82, 64, 42], 17, 10)
    readout(panel.get("prisoners").surf, [
        ("Held", "02", GREEN), ("Krell", "01", YELLOW), ("Trader", "01", GREEN),
        ("Risk", "LOW", GREEN), ("Guard", "BETA", GREEN),
    ], 6, 8, 17, 11, 60)
    text_rows(panel.get("interrogations").surf, [
        ("QUEUE", "cyan"), ("KR-17 00:12 hold", "yellow"),
        ("MN-04 00:35 witness", "green"), ("LOG SEALED", "cyan"),
        ("NEXT: sec chief", "green"),
    ], 6, 8, 17, 10)


def _draw_log():
    disp = P["Commanders Log"].get("log")
    text_rows(disp.surf, [
        ("IMPERIAL TRIBUNE", "cyan"), ("STARDATE 7421.6", "green"),
        ("Klagar-class", "green"), ("battlecruiser docked", "green"),
        ("at Starfort SF-1.", "green"), ("Stores: 24 torpedoes,", "green"),
        ("4000 power units,", "green"), ("1000 tons supplies.", "green"),
        ("150 shock troops ready.", "yellow"), ("", "green"),
        ("Standing order:", "cyan"), ("complete training", "cyan"),
        ("patrol and report.", "cyan"),
    ], 8, 8, 18, 11)
