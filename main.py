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
  r / [ ]        plot course / adjust course
  F1 / Ctrl+H    toggle control help
  F2-F5          set ship damage state
  Ctrl+1-4       fallback damage keys for media-key keyboards
  d f g h j      combat overlays (menu, grid, heading, target, line)
  k              toggle Computer Display combat stats view
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
        self.notepad_visible = False
        self.notepad_buffer = ""
        self.notepad_cursor = 0
        self.notepad_saved_snapshot = ""
        self.notepad_menu_visible = False
        self.notepad_confirm_discard = False
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
        if self.notepad_visible:
            self.notepad_click(pos)
            return
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
        if self.display_click(point):
            return
        if self.notepad_rect().collidepoint(point):
            self.open_notepad()

    def hover(self, pos):
        if self.help_visible:
            for button in BUTTONS:
                button.hover = False
            return
        point = self.to_canvas(pos)
        for button in BUTTONS:
            button.hover = point is not None and button.screen_rect.collidepoint(point)

    def side_effects(self, button):
        self._handle_global_button(button)
        if button.panel is cockpit.P["Navigation"]:
            self._handle_navigation_button(button)
        elif button.panel is cockpit.P["Primary Display"]:
            self._handle_primary_button(button)
        elif button.panel is cockpit.P["Engineering Console"]:
            self._handle_engineering_button(button)
        elif button.panel is cockpit.P["Science Console"]:
            self._handle_science_button(button)
        elif button.panel is cockpit.P["Computer Display"]:
            self._handle_computer_button(button)
        elif button.panel is cockpit.P["Combat Console"]:
            self._handle_combat_button(button)

    def _handle_global_button(self, button):
        if button.label == "Send Message":
            self.state.add_message("Comms", "message queued for fleet relay")
            button.active = False
        if button.label == "SNAP":
            button.active = False
            self.snapshot_pending = True
        if button.label == "Help F1/Ctrl+H":
            button.active = False
            self.help_visible = True

    def _handle_navigation_button(self, button):
        if button.label == "Evasive":
            self.state.set_nav_evasive(button.active)
        elif button.label == "<<":
            self.state.adjust_nav_sideslip(-1)
            button.active = False
        elif button.label == ">>":
            self.state.adjust_nav_sideslip(1)
            button.active = False

    def display_click(self, point):
        if cockpit.reference_library_click(point):
            return True

        nav_panel = cockpit.P["Navigation"]
        nav_readout = nav_panel.get("nav readout")
        nav_rect = pygame.Rect(nav_panel.x + nav_readout.pos[0],
                               nav_panel.y + nav_readout.pos[1],
                               nav_readout.size[0], nav_readout.size[1])
        if nav_rect.collidepoint(point):
            local_y = point[1] - nav_rect.y
            if 58 <= local_y <= 102:
                self.state.plot_course_to_target()
                return True
            if 103 <= local_y <= 124:
                self.state.target_next_contact()
                self.state.plot_course_to_target()
                return True
            return False

        console = cockpit.P["Navigation Console"]
        system = console.get("system")
        system_rect = pygame.Rect(console.x + system.pos[0], console.y + system.pos[1],
                                  system.size[0], system.size[1])
        if system_rect.collidepoint(point):
            local_x = point[0] - system_rect.x
            local_y = point[1] - system_rect.y
            cx, cy = system.rect.center
            system_x = self.state.system_x + (local_x - cx) / 5.0
            system_y = self.state.system_y + (local_y - cy) / 5.0
            self.state.select_nav_point(system_x, system_y)
            return True
        return False

    def _handle_primary_button(self, button):
        if button.label == "REST":
            self.state.toggle_rest(button.active)
        elif button.label == "Sim Freeze":
            self.state.toggle_sim_freeze(button.active)

    def _handle_engineering_button(self, button):
        if button.label == "Launch":
            self.state.launch_probe()
            button.active = False

    def _handle_science_button(self, button):
        if button.label in ("SRS", "LRS"):
            self.state.set_science_scope(button.label)
            button.active = False
        elif button.label in ("Dept Q", "Planet Data"):
            self.state.set_science_page(button.label)
        elif button.label == "Board":
            self.state.attempt_boarding()
            button.active = False

    def _handle_computer_button(self, button):
        if button.group == "computer_menu":
            if button.label == "Self-Destruct":
                self.state.activate_self_destruct()
            else:
                if button.label == "Reference Lib":
                    cockpit.P["Computer Display"].reference_topic = None
                self.state.set_computer_page(button.label)

    def _handle_combat_button(self, button):
        if button.label in ("BCS", "SCS"):
            self.state.set_combat_alignment(button.label)
        elif button.label in ("SRS", "LRS"):
            self.state.set_science_scope(button.label)
            button.active = False
        elif button.label in ("Dept Q", "Planet Data"):
            self.state.set_science_page(button.label)
        elif button.label in self.state.weapons:
            self.state.select_weapon(button.label)
        elif button.label == "ECM":
            self.state.toggle_ecm(button.active)
        elif button.label in ("Ph", "T1", "T2"):
            self.state.select_weapon({"Ph": "Phaser", "T1": "Trp1", "T2": "Trp2"}[button.label])
            self.state.set_weapon_condition("Auto")
        elif button.label == "Cont":
            self.state.set_weapon_condition("Cont")
        elif button.label in ("Auto", "Manual", "Battle Entry", "Maximum"):
            self.state.set_shield_mode(button.label)
        elif button.label == "Board":
            self.state.attempt_boarding()
            button.active = False

    def key(self, event):
        ctrl_down = bool(getattr(event, "mod", 0) & KMOD_CTRL)
        if self.notepad_visible:
            self.notepad_key(event)
            return
        if ctrl_down and event.key == pygame.K_n:
            self.open_notepad()
            return
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
            if st.energy_usage == 100:
                return
            st.change_hyper_velocity(1)
        elif key == pygame.K_x:
            if st.energy_usage == 20:
                return
            st.change_hyper_velocity(-1)
        elif key == pygame.K_c:
            if st.energy_usage == 100:
                return
            st.change_space_velocity(1)
        elif key == pygame.K_v:
            if st.energy_usage == 20:
                return
            st.change_space_velocity(-1)
        elif key == pygame.K_r:
            st.plot_course_to_target()
        elif key == pygame.K_k:
            computer = cockpit.P["Computer Display"]
            if computer.computer_mode == "combat stats":
                computer.computer_combat_view = (
                    "k" if getattr(computer, "computer_combat_view", "e") == "e" else "e"
                )
        elif key == pygame.K_LEFTBRACKET:
            st.set_nav_course(st.set_course - 15)
        elif key == pygame.K_RIGHTBRACKET:
            st.set_nav_course(st.set_course + 15)
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

    # --- notepad --------------------------------------------------------

    def notepad_rect(self):
        return pygame.Rect((CANVAS_SIZE[0] - self.notepad.size[0]) // 2, 1015,
                           self.notepad.size[0], self.notepad.size[1])

    def open_notepad(self):
        self.notepad_visible = True
        self.notepad_buffer = self.state.notepad_text
        self.notepad_saved_snapshot = self.state.notepad_text
        self.notepad_cursor = len(self.notepad_buffer)
        self.notepad_menu_visible = False
        self.notepad_confirm_discard = False
        pygame.key.start_text_input()

    def save_notepad(self):
        self.state.notepad_text = self.notepad_buffer
        self.notepad_saved_snapshot = self.notepad_buffer
        self.notepad_visible = False
        self.notepad_menu_visible = False
        self.notepad_confirm_discard = False
        pygame.key.stop_text_input()
        self.state.add_message("NotePad", "notes saved")

    def discard_notepad(self):
        self.notepad_buffer = self.notepad_saved_snapshot
        self.notepad_visible = False
        self.notepad_menu_visible = False
        self.notepad_confirm_discard = False
        pygame.key.stop_text_input()
        self.state.add_message("NotePad", "notes discarded")

    def notepad_click(self, pos):
        point = self.to_canvas(pos)
        if point is None:
            return
        editor = self.notepad_editor_rect()
        if editor.collidepoint(point):
            rel_y = int((point[1] - editor.y - 8) // 17)
            rel_x = int((point[0] - editor.x - 8) // 9)
            lines = self.notepad_lines()
            line = max(0, min(len(lines) - 1, rel_y))
            col = max(0, min(len(lines[line]), rel_x))
            self.notepad_cursor = self.notepad_index_from_line_col(line, col)

    def notepad_key(self, event):
        ctrl_down = bool(getattr(event, "mod", 0) & KMOD_CTRL)
        if self.notepad_menu_visible and not ctrl_down:
            self.notepad_menu_visible = False
            return
        if self.notepad_confirm_discard:
            if event.key == pygame.K_y:
                self.discard_notepad()
            elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                self.notepad_confirm_discard = False
            return
        if ctrl_down and event.key == pygame.K_s:
            self.save_notepad()
        elif ctrl_down and event.key == pygame.K_m:
            self.notepad_menu_visible = True
        elif ctrl_down and event.key == pygame.K_HOME:
            self.notepad_cursor = 0
        elif ctrl_down and event.key == pygame.K_END:
            self.notepad_buffer = ""
            self.notepad_cursor = 0
        elif event.key == pygame.K_ESCAPE:
            if self.notepad_buffer != self.notepad_saved_snapshot:
                self.notepad_confirm_discard = True
            else:
                self.discard_notepad()
        elif event.key == pygame.K_RETURN:
            self.notepad_insert("\n")
        elif event.key == pygame.K_BACKSPACE:
            if self.notepad_cursor > 0:
                self.notepad_buffer = (self.notepad_buffer[:self.notepad_cursor - 1] +
                                       self.notepad_buffer[self.notepad_cursor:])
                self.notepad_cursor -= 1
        elif event.key == pygame.K_DELETE:
            if self.notepad_cursor < len(self.notepad_buffer):
                self.notepad_buffer = (self.notepad_buffer[:self.notepad_cursor] +
                                       self.notepad_buffer[self.notepad_cursor + 1:])
        elif event.key == pygame.K_LEFT:
            self.notepad_cursor = max(0, self.notepad_cursor - 1)
        elif event.key == pygame.K_RIGHT:
            self.notepad_cursor = min(len(self.notepad_buffer), self.notepad_cursor + 1)
        elif event.key == pygame.K_UP:
            self.notepad_move_vertical(-1)
        elif event.key == pygame.K_DOWN:
            self.notepad_move_vertical(1)
        elif event.key == pygame.K_HOME:
            line, _ = self.notepad_line_col()
            self.notepad_cursor = self.notepad_index_from_line_col(line, 0)
        elif event.key == pygame.K_END:
            line, _ = self.notepad_line_col()
            self.notepad_cursor = self.notepad_index_from_line_col(line, len(self.notepad_lines()[line]))
        else:
            text = getattr(event, "unicode", "")
            if text and text.isprintable() and not ctrl_down:
                self.notepad_insert(text)

    def notepad_insert(self, text):
        lines = self.notepad_lines()
        line, col = self.notepad_line_col()
        if text == "\n":
            if len(lines) >= 22:
                return
        elif len(lines[line]) >= 74:
            return
        new_text = self.notepad_buffer[:self.notepad_cursor] + text + self.notepad_buffer[self.notepad_cursor:]
        new_lines = new_text.split("\n")
        if len(new_lines) <= 22 and all(len(row) <= 74 for row in new_lines):
            self.notepad_buffer = new_text
            self.notepad_cursor += len(text)

    def notepad_lines(self):
        return self.notepad_buffer.split("\n") or [""]

    def notepad_line_col(self):
        before = self.notepad_buffer[:self.notepad_cursor]
        line = before.count("\n")
        last_break = before.rfind("\n")
        col = len(before) if last_break < 0 else len(before) - last_break - 1
        return line, col

    def notepad_index_from_line_col(self, line, col):
        lines = self.notepad_lines()
        line = max(0, min(len(lines) - 1, line))
        col = max(0, min(len(lines[line]), col))
        return sum(len(lines[i]) + 1 for i in range(line)) + col

    def notepad_move_vertical(self, delta):
        line, col = self.notepad_line_col()
        lines = self.notepad_lines()
        line = max(0, min(len(lines) - 1, line + delta))
        self.notepad_cursor = self.notepad_index_from_line_col(line, min(col, len(lines[line])))

    def notepad_editor_rect(self):
        return pygame.Rect(500, 250, 920, 520)

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
        if self.help_visible or self.notepad_visible:
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
        if self.notepad_visible:
            self.draw_notepad(now)
        if self.snapshot_pending:
            self.save_snapshot()
        self.blit_scaled()

    def draw_notepad(self, current_time):
        overlay = pygame.Surface(CANVAS_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        self.canvas.blit(overlay, (0, 0))

        rect = self.notepad_editor_rect()
        pygame.draw.rect(self.canvas, core.PANEL_BG, rect)
        pygame.draw.line(self.canvas, core.BEVEL_LIGHT, rect.topleft, rect.topright, 2)
        pygame.draw.line(self.canvas, core.BEVEL_LIGHT, rect.topleft, rect.bottomleft, 2)
        pygame.draw.line(self.canvas, core.BEVEL_DARK, rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(self.canvas, core.BEVEL_DARK, rect.topright, rect.bottomright, 2)
        title = pygame.Rect(rect.x + 8, rect.y + 8, rect.w - 16, 28)
        core.fit_text(self.canvas, "NOTE PAD", title, core.BLACK, 22, align="left")
        core.fit_text(self.canvas, "Ctrl+S Save   Esc Exit   Ctrl+M Menu",
                      title, core.CYAN, 12, align="right")

        paper = pygame.Rect(rect.x + 14, rect.y + 44, rect.w - 28, rect.h - 82)
        pygame.draw.rect(self.canvas, core.BLACK, paper)
        pygame.draw.rect(self.canvas, core.FRAME_DIM, paper, 1)
        lines = self.notepad_lines()
        font = core.font(14, True)
        for i, line in enumerate(lines[:22]):
            y = paper.y + 8 + i * 17
            label = font.render(line, True, core.GREEN)
            self.canvas.blit(label, (paper.x + 8, y))

        line, col = self.notepad_line_col()
        if (current_time // 350) % 2 == 0:
            cx = paper.x + 8 + col * 9
            cy = paper.y + 8 + line * 17
            pygame.draw.line(self.canvas, core.WHITE, (cx, cy), (cx, cy + 14), 1)

        status = pygame.Rect(rect.x + 14, rect.bottom - 32, rect.w - 28, 18)
        dirty = "MODIFIED" if self.notepad_buffer != self.notepad_saved_snapshot else "SAVED"
        core.fit_text(self.canvas, f"{dirty}   Lines {len(lines)}/22   Col {col + 1}/74",
                      status, core.YELLOW if dirty == "MODIFIED" else core.GREEN, 11, align="left")

        if self.notepad_menu_visible:
            menu = pygame.Rect(rect.centerx - 240, rect.centery - 105, 480, 210)
            pygame.draw.rect(self.canvas, core.PANEL_BG, menu)
            pygame.draw.rect(self.canvas, core.FRAME, menu, 2)
            rows = [
                "NOTE PAD MENU",
                "Ctrl+S   Save notes and exit",
                "Esc      Exit without saving after confirmation",
                "Ctrl+End Clear the note pad",
                "Ctrl+Home Move cursor to upper-left",
                "Enter    Insert blank line",
                "Any key  Close this menu",
            ]
            for i, row in enumerate(rows):
                fg = core.CYAN if i == 0 else core.BLACK
                core.fit_text(self.canvas, row, [menu.x + 16, menu.y + 12 + i * 26,
                              menu.w - 32, 22], fg, 14, align="left")

        if self.notepad_confirm_discard:
            prompt = pygame.Rect(rect.centerx - 240, rect.centery - 44, 480, 88)
            pygame.draw.rect(self.canvas, core.PANEL_BG, prompt)
            pygame.draw.rect(self.canvas, core.RED, prompt, 2)
            core.fit_text(self.canvas, "Exit without saving changes?",
                          [prompt.x + 12, prompt.y + 12, prompt.w - 24, 24],
                          core.RED, 15)
            core.fit_text(self.canvas, "Y = discard notes     N/Esc = return",
                          [prompt.x + 12, prompt.y + 48, prompt.w - 24, 22],
                          core.BLACK, 13)

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
                elif event.type == KEYDOWN and self.notepad_visible:
                    self.key(event)
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
