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
    """Lightweight warp-streak animation used when no video backend exists."""

    def __init__(self, size, label):
        self.size = size
        self.label = label
        w, h = size
        self.stars = [[random.uniform(0, w), random.uniform(0, h),
                       random.uniform(0.5, 2.5)] for _ in range(120)]

    def update_draw(self, surface):
        w, h = self.size
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
        if not (self.players and self.index < len(self.players)):
            self.fallback.update_draw(self.surf)
        pygame.draw.rect(self.surf, FRAME, self.rect, 1)
        self.panel.surf.blit(self.surf, self.pos)

    def update(self, events):
        if self.players and self.index < len(self.players):
            self.players[self.index].draw(self.surf)
            self.players[self.index].update(events)

    def close(self):
        for player in self.players:
            try:
                player.close()
            except Exception:
                pass
