"""Star Fleet II Deluxe cockpit UI.

A production-style command screen rendered with pygame. Panels, readouts, and
buttons emulate the Krellan battlecruiser interface. Every on-screen button
responds to both mouse clicks and its keyboard shortcut.

Controls:
  Esc            close help / quit
  F11            toggle fullscreen / windowed
  Mouse click    activate any button
  1-8            latch top alert indicators
  i o p          navigation console views
  l ; '          star map views
  q w            engineering probe views
  z x / c v      raise / lower hyperspace and normal-space velocity
  F1 / Ctrl+H    toggle control help
  F2-F5          set ship damage state
  Ctrl+1-4       fallback damage keys for media-key keyboards
  d f g h j      combat overlays (menu, grid, heading, target, line)
  m , . /        shield modes
  Left / Right   select weapon
  9 0 -          communication feed (messages, reports, combined)
  n              cycle primary display clip
  Right Shift    target board
"""

import pygame
from datetime import datetime
import os
from pygame.locals import (FULLSCREEN, HWSURFACE, DOUBLEBUF, QUIT, KEYDOWN,
                           MOUSEBUTTONDOWN, MOUSEMOTION, K_F11, K_ESCAPE,
                           KMOD_CTRL)

import core
import cockpit
import help_screen
import widgets
from widgets import StatusBar, BUTTONS
from state import ShipState

CANVAS_SIZE = (1920, 1080)
WINDOWED_SIZE = (1680, 945)
FPS = 60
SNAPSHOT_DIR = os.path.join(core.BASE_DIR, "snapshots")


class Cockpit:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Star Fleet II Deluxe")
        self.clock = pygame.time.Clock()
        self.fullscreen = True
        self.help_visible = False
        self.snapshot_pending = False
        self.display = pygame.display.set_mode((0, 0), pygame.RESIZABLE | HWSURFACE | DOUBLEBUF)
        self.canvas = pygame.Surface(CANVAS_SIZE).convert()
        self.last_tick = pygame.time.get_ticks()

        self.state = ShipState()
        widgets.reset_buttons()
        self.panels = cockpit.build()
        self.top_bars = StatusBar.make_top()
        self.menu_bars = StatusBar.make_menu()
        self.notepad = StatusBar("NotePad")
        self.key_buttons = {b.key: b for b in BUTTONS if b.key is not None}

        self.primary = cockpit.P["Primary Display"].get("primary")

    # --- input ----------------------------------------------------------

    def to_canvas(self, pos):
        """Map a display-space mouse point onto canvas coordinates."""
        view = self.canvas.get_rect().fit(self.display.get_rect())
        view.center = self.display.get_rect().center
        if not view.collidepoint(pos):
            return None
        sx = CANVAS_SIZE[0] / view.width
        sy = CANVAS_SIZE[1] / view.height
        return ((pos[0] - view.x) * sx, (pos[1] - view.y) * sy)

    def click(self, pos):
        if self.help_visible:
            return
        point = self.to_canvas(pos)
        if point is None:
            return
        for button in BUTTONS:
            if button.screen_rect.collidepoint(point):
                button.activate()
                self.side_effects(button)
                return

    def hover(self, pos):
        if self.help_visible:
            for button in BUTTONS:
                button.hover = False
            return
        point = self.to_canvas(pos)
        for button in BUTTONS:
            button.hover = point is not None and button.screen_rect.collidepoint(point)

    def side_effects(self, button):
        if button.label == "Send Message":
            self.state.add_message("Comms", "message queued for fleet relay")
            button.active = False
        if button.label == "SNAP":
            button.active = False
            self.snapshot_pending = True
        if button.label == "Help F1/Ctrl+H":
            button.active = False
            self.help_visible = True
        if button.panel is cockpit.P["Navigation"]:
            if button.label == "Evasive":
                self.state.set_nav_evasive(button.active)
            elif button.label == "<<":
                self.state.adjust_nav_sideslip(-1)
                button.active = False
            elif button.label == ">>":
                self.state.adjust_nav_sideslip(1)
                button.active = False
        if button.panel is cockpit.P["Primary Display"] and button.label == "REST":
            self.state.toggle_rest(button.active)
        if button.panel is cockpit.P["Primary Display"] and button.label == "Sim Freeze":
            self.state.toggle_sim_freeze(button.active)
        if button.panel is cockpit.P["Engineering Console"] and button.label == "Launch":
            self.state.launch_probe()
            button.active = False
        if button.panel is cockpit.P["Combat Console"]:
            if button.label in ("Auto", "Manual", "Battle Entry", "Maximum"):
                self.state.set_shield_mode(button.label)
            elif button.label == "Board":
                self.state.attempt_boarding()
                button.active = False

    def key(self, event):
        ctrl_down = bool(getattr(event, "mod", 0) & KMOD_CTRL)
        if event.key == pygame.K_F1 or (ctrl_down and event.key == pygame.K_h):
            self.help_visible = not self.help_visible
            return
        if self.help_visible:
            return
        if event.key == K_F11:
            self.toggle_fullscreen()
            return
        if event.key in self.key_buttons:
            button = self.key_buttons[event.key]
            button.activate()
            self.side_effects(button)
            return
        self.special_key(event)

    def special_key(self, event):
        st = self.state
        key = event.key
        ctrl_down = bool(getattr(event, "mod", 0) & KMOD_CTRL)
        if ctrl_down and pygame.K_1 <= key <= pygame.K_4:
            st.set_damage_level(key - pygame.K_1 + 1)
        elif pygame.K_1 <= key <= pygame.K_8:
            self.top_bars[key - pygame.K_1].alerting ^= True
        elif key == pygame.K_z:
            st.change_hyper_velocity(1)
        elif key == pygame.K_x:
            st.change_hyper_velocity(-1)
        elif key == pygame.K_c:
            st.change_space_velocity(1)
        elif key == pygame.K_v:
            st.change_space_velocity(-1)
        elif key in (pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5):
            st.set_damage_level({pygame.K_F2: 1, pygame.K_F3: 2,
                                 pygame.K_F4: 3, pygame.K_F5: 4}[key])
        elif key == pygame.K_RIGHT:
            st.cycle_weapon(1)
        elif key == pygame.K_LEFT:
            st.cycle_weapon(-1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            st.fire_selected_weapon()
        elif key == pygame.K_t:
            st.target_next_contact()
        elif key == pygame.K_n:
            self.primary.cycle()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.display = pygame.display.set_mode((0, 0), FULLSCREEN | HWSURFACE | DOUBLEBUF)
        else:
            self.display = pygame.display.set_mode(WINDOWED_SIZE, HWSURFACE | DOUBLEBUF)

    # --- frame ----------------------------------------------------------

    def render(self, events):
        now = pygame.time.get_ticks()
        dt = (now - self.last_tick) / 1000.0
        self.last_tick = now
        self.state.tick(dt)
        # pyvidplayer2 assigns F1 to mute. It must not receive the cockpit's
        # help shortcut, including the second press that closes the overlay.
        video_events = [event for event in events
                        if not (event.type == KEYDOWN and event.key == pygame.K_F1)]
        if self.help_visible:
            video_events = []
        self.canvas.fill(core.SHELL_BG)
        for panel in self.panels:
            panel.draw_base()
        cockpit.draw(self.state, now)
        self.primary.update(video_events)
        for panel in self.panels:
            panel.finish(self.canvas)
        for bar in self.top_bars:
            bar.alerting = self.state.status_flags.get(bar.label, False)
        StatusBar.sequence_flash(self.top_bars)
        StatusBar.draw_bars(self.canvas, self.top_bars, self.menu_bars, self.notepad)
        if self.help_visible:
            help_screen.draw(self.canvas)
        if self.snapshot_pending:
            self.save_snapshot()
        self.blit_scaled()

    def save_snapshot(self):
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        path = os.path.join(SNAPSHOT_DIR, f"starfleet_{stamp}.png")
        pygame.image.save(self.canvas, path)
        self.snapshot_pending = False
        print(f"Saved snapshot: {path}")

    def blit_scaled(self):
        view = self.canvas.get_rect().fit(self.display.get_rect())
        if view.size == CANVAS_SIZE:
            self.display.blit(self.canvas, (0, 0))
        else:
            view.center = self.display.get_rect().center
            self.display.fill(core.SHELL_BG)
            self.display.blit(pygame.transform.smoothscale(self.canvas, view.size), view)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    if self.help_visible:
                        self.help_visible = False
                    else:
                        running = False
                elif event.type == KEYDOWN:
                    self.key(event)
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.click(event.pos)
                elif event.type == MOUSEMOTION:
                    self.hover(event.pos)
            self.render(events)
            self.clock.tick(FPS)
        self.primary.close()


if __name__ == "__main__":
    Cockpit().run()
