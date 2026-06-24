"""Primary and navigation video displays with a no-dependency fallback.

If pyvidplayer2 and ffmpeg are present, the configured clips play. Otherwise
an animated starfield keeps the screen alive so the cockpit still runs.
"""

import os
import random
import pygame
import core
from core import ASSET_DIR, FRAME, CYAN

try:
    import pyvidplayer2
    HAVE_VIDEO = True
except Exception:
    HAVE_VIDEO = False


class _Starfield:
    """Lightweight animated display used when no video backend exists."""

    def __init__(self, size, label):
        self.size = size
        self.label = label
        w, h = size
        rng = random.Random(74216)
        self.stars = [[rng.uniform(0, w), rng.uniform(0, h),
                       rng.uniform(0.5, 2.5)] for _ in range(120)]
        self.map_surface = self._make_world_map()

    def _make_world_map(self):
        w, h = self.size
        surf = pygame.Surface(self.size).convert()
        surf.fill((36, 82, 112))
        rng = random.Random(1470940)
        land = pygame.Surface(self.size, pygame.SRCALPHA)
        continents = [
            [(72, 74), (126, 40), (176, 68), (156, 132), (96, 146), (48, 108)],
            [(220, 48), (332, 42), (390, 92), (354, 152), (262, 148), (196, 96)],
            [(405, 112), (510, 98), (596, 142), (562, 230), (442, 246), (388, 182)],
            [(186, 184), (250, 172), (286, 236), (244, 296), (182, 264)],
            [(520, 236), (610, 226), (630, 292), (540, 304)],
        ]
        sx = w / 645
        sy = h / 320
        for poly in continents:
            pts = [(int(x * sx), int(y * sy)) for x, y in poly]
            pygame.draw.polygon(land, (54, 132, 42, 235), pts)
            pygame.draw.polygon(land, (108, 118, 72, 150), pts, 2)
        for _ in range(44):
            x = rng.randrange(0, max(1, w - 30))
            y = rng.randrange(0, max(1, h - 20))
            ww = rng.randrange(16, 56)
            hh = rng.randrange(8, 28)
            col = (66 + rng.randrange(35), 124 + rng.randrange(55), 40 + rng.randrange(30), 115)
            pygame.draw.ellipse(land, col, (x, y, ww, hh))
        surf.blit(land, (0, 0))
        shade = pygame.Surface(self.size, pygame.SRCALPHA)
        for y in range(h):
            alpha = int(42 * abs(y - h / 2) / (h / 2))
            pygame.draw.line(shade, (0, 0, 0, alpha), (0, y), (w, y))
        surf.blit(shade, (0, 0))
        return surf

    def update_draw(self, surface):
        w, h = self.size
        if self.label == "EARTH ORBIT":
            surface.blit(self.map_surface, (0, 0))
            core.text_line(surface, self.label, (8, 6), CYAN, 12)
            return
        surface.fill((4, 6, 16))
        for star in self.stars:
            star[0] -= star[2] * 2.2
            if star[0] < 0:
                star[0] = w
                star[1] = random.uniform(0, h)
            shade = int(90 + star[2] * 55)
            pygame.draw.line(surface, (shade, shade, min(255, shade + 40)),
                             (star[0], star[1]), (star[0] + star[2] * 3, star[1]), 1)
        core.text_line(surface, self.label, (8, 6), CYAN, 12)


class VideoDisplay:
    """Cycles a list of clips on a panel display, with a starfield fallback."""

    def __init__(self, panel, label, size, pos):
        self.panel = panel
        self.label = label
        self.size = size
        self.pos = pos
        self.surf = pygame.Surface(size).convert()
        self.rect = self.surf.get_rect()
        self.sources = []
        self.players = []
        self.fallback = _Starfield(size, "DEEP SPACE")
        self.index = 0
        self.use_fallback_frame = False
        self.z = 1
        panel.add(self)

    def prepare(self):
        pass

    def set_videos(self, names):
        self.sources = names
        self.players = []
        if not HAVE_VIDEO:
            return
        for name in names:
            try:
                clip = pyvidplayer2.Video(os.path.join(ASSET_DIR, name))
                clip.stop()
                self.players.append(pyvidplayer2.VideoPlayer(clip, self.rect, loop=True))
            except Exception:
                pass

    def cycle(self):
        count = len(self.players) if self.players else max(1, len(self.sources))
        self.index = (self.index + 1) % count
        labels = ["DEEP SPACE", "EARTH ORBIT", "MERCATOR MAP"]
        self.fallback.label = labels[self.index % len(labels)]

    def draw(self):
        if self.use_fallback_frame or not (self.players and self.index < len(self.players)):
            self.fallback.update_draw(self.surf)
        pygame.draw.rect(self.surf, FRAME, self.rect, 1)
        self.panel.surf.blit(self.surf, self.pos)

    def update(self, events):
        if self.players and self.index < len(self.players):
            self.players[self.index].draw(self.surf)
            self.players[self.index].update(events)
            avg = pygame.transform.average_color(self.surf)
            self.use_fallback_frame = sum(avg[:3]) < 18

    def close(self):
        for player in self.players:
            try:
                player.close()
            except Exception:
                pass
