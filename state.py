"""Mutable runtime state for the cockpit, separated from drawing code."""

import math
import random


class ShipState:
    """All values the consoles read and the input layer mutates."""

    TOP_ALERT_LABELS = ["LowPwr", "LowSup", "LowTime", "Medical",
                        "SecAlt", "Mines", "Distress", "HullPn"]

    def __init__(self):
        self.rng = random.Random(74216)

        # Mission clock and tactical posture.
        self.mission_elapsed_days = 15.24
        self.time_left_days = 5.26
        self.alert_status = "Green"
        self.rest_mode = False
        self.sim_frozen = False

        # Ship position and navigation.
        self.region_x = 4.0
        self.region_y = 6.0
        self.system_x = 40.0
        self.system_y = 23.0
        self.set_course = 135.0
        self.actual_heading = self.set_course
        self.nav_object = "Planet"
        self.nav_evasive = False
        self.nav_sideslip = 0
        self._evasive_phase = 0.0
        self.docked = False
        self.in_orbit = True

        # Engineering and stores.
        self.hyper_velocity = 0
        self.space_velocity = 0
        self.damage_level = 1
        self.energy_capacity = 4000
        self.energy_units = 4000.0
        self.backup_energy_pct = 100
        self.supplies = 1000
        self.torpedoes = 24
        self.probe_loaded = 5
        self.probe_storage = 5
        self.pods = 2
        self.escorts = 4
        self.crew = 275
        self.shock_troops = 150
        self.prisoners = 0
        self.marines = 1
        self.medical_cases = 0
        self.hull_pct = 100

        # Combat systems.
        self.weapon_index = 0
        self.weapons = ["Phaser", "Trp1", "Trp2", "ObltrPd"]
        self.weapon_reload = [0.0, 0.0, 0.0, 0.0]
        self.weapon_auto = True
        self.weapon_destroy = True
        self.ecm_enabled = False
        self.cmf_enabled = False
        self.tractor_enabled = False

        # Defensive systems. AAS owns automatic shield/alert changes.
        self.aas_enabled = False
        self.shield_policy = "Manual"
        self.shields_up = True
        self.shield_strength = [500, 2000, 1000, 0]

        # Communication feed scroll position.
        self.feed_index = 1
        self.feed_clock = 0
        self.messages = [
            ("Executive Off.", "Klagar-class battlecruiser ready"),
            ("Starfort SF-1", "24 torps / 4000 power loaded"),
            ("Fleet Command", "training patrol assigned"),
            ("Damage Control", "shields and tractor beam nominal"),
            ("Probe Control", "L:5 S:5 sensor probes loaded"),
            ("Landing Party", "150 shock troops aboard"),
            ("Strategic Cmd", "4 destroyer escorts standing by"),
        ]
        self.reports = [
            ("NAV-006", "docked at region 6,0"),
            ("ENG-4000", "power reserve 4000 units"),
            ("CMB-024", "torpedo stores full"),
            ("DATA-1000", "supplies 1000 tons"),
            ("TRP-150", "shock troops ready"),
            ("SCI-L5S5", "sensor probes loaded"),
            ("STG-004", "destroyer escort screen"),
        ]

        self.contacts = [
            {"id": "SF-1", "name": "Starfort", "kind": "base", "x": 42.0, "y": 20.0,
             "region": (4, 6), "threat": False, "shields_up": False, "prisoners": 0},
            {"id": "TRUTH", "name": "Truth", "kind": "planet", "x": 47.0, "y": 17.0,
             "region": (4, 6), "threat": False, "shields_up": False, "prisoners": 0},
            {"id": "EN-1", "name": "Krell Raider", "kind": "ship", "x": 37.0, "y": 27.0,
             "region": (4, 6), "threat": True, "shields_up": True, "prisoners": 2},
            {"id": "MN-1", "name": "Minefield", "kind": "mine", "x": 43.0, "y": 31.0,
             "region": (4, 6), "threat": True, "shields_up": False, "prisoners": 0},
        ]
        self.target_index = 1
        self.active_probes = []
        self.status_flags = {}
        self.energy_usage = 20
        self._sync_systems()
        self._sync_navigation()

    @property
    def selected_weapon(self):
        return self.weapons[self.weapon_index]

    @property
    def selected_target(self):
        return self.contacts[self.target_index % len(self.contacts)]

    @property
    def energy_pct(self):
        return max(0, min(100, round(self.energy_units / self.energy_capacity * 100)))

    @property
    def shield_pct(self):
        return max(0, min(100, round(sum(self.shield_strength) / 3500 * 100)))

    @property
    def energy_color(self):
        if self.energy_usage > 70 or self.energy_pct < 25:
            return "red"
        if self.energy_usage > 35 or self.energy_pct < 45:
            return "yellow"
        return "green"

    def tick(self, dt):
        if self.sim_frozen:
            return
        dt = max(0.0, min(float(dt), 0.25))
        self._evasive_phase += dt
        self._sync_systems()
        self._move_ship(dt)
        self._drain_energy(dt)
        self._reload_weapons(dt)
        self._advance_clock(dt)
        self._update_probe_tracks(dt)
        self._sync_systems()
        self._sync_navigation()

    def toggle_rest(self, active=None):
        self.rest_mode = (not self.rest_mode) if active is None else bool(active)
        self.add_message("Executive Off.", "rest cycle engaged" if self.rest_mode else "rest cycle cancelled")

    def toggle_sim_freeze(self, active=None):
        self.sim_frozen = (not self.sim_frozen) if active is None else bool(active)
        self.add_message("Computer", "simulation frozen" if self.sim_frozen else "simulation resumed")

    def set_damage_level(self, level):
        self.damage_level = max(1, min(4, int(level)))
        self.hull_pct = {1: 100, 2: 72, 3: 38, 4: 0}[self.damage_level]
        self.add_message("Damage Control", f"hull condition level {self.damage_level}")

    def change_hyper_velocity(self, delta):
        if self.damage_level >= 4:
            self.add_message("Engineering", "hyperdrive inoperative")
            return
        old = self.hyper_velocity
        self.hyper_velocity = max(0, min(10, self.hyper_velocity + int(delta)))
        if self.hyper_velocity != old:
            self.in_orbit = False
            self.docked = False
            self.add_message("Helm", f"hyper velocity {self.hyper_velocity}")

    def change_space_velocity(self, delta):
        if self.damage_level >= 3:
            self.add_message("Engineering", "sublight engines degraded")
            if delta > 0 and self.space_velocity >= 5:
                return
        old = self.space_velocity
        self.space_velocity = max(0, min(10, self.space_velocity + int(delta)))
        if self.space_velocity != old:
            self.in_orbit = False
            self.docked = False
            self.add_message("Helm", f"sublight velocity {self.space_velocity}")

    def set_nav_evasive(self, active):
        self.nav_evasive = bool(active)
        self.add_message("Navigation", "evasive course enabled" if active else "evasive course cancelled")
        self._sync_navigation()

    def adjust_nav_sideslip(self, amount):
        amount = int(amount)
        self.nav_sideslip = max(-9, min(9, self.nav_sideslip + amount))
        if amount:
            side = "port" if amount < 0 else "starboard"
            self.add_message("Navigation", f"sideslip {side} vector set")
        self._sync_navigation()

    def cycle_weapon(self, delta):
        self.weapon_index = (self.weapon_index + int(delta)) % len(self.weapons)
        self.add_message("Weapons", f"{self.selected_weapon} selected")

    def fire_selected_weapon(self):
        idx = self.weapon_index
        if self.weapon_reload[idx] > 0:
            self.add_message("Weapons", f"{self.selected_weapon} not ready")
            return False
        if self.ecm_enabled:
            self.add_message("Weapons", "ECM blocks target lock")
            return False
        if idx in (1, 2, 3) and self.torpedoes <= 0:
            self.add_message("Weapons", "torpedo stores empty")
            return False
        if idx in (1, 2, 3):
            self.torpedoes -= 1
        self.weapon_reload[idx] = [2.0, 5.0, 5.0, 8.0][idx]
        self.add_message("Weapons", f"{self.selected_weapon} fired at {self.selected_target['name']}")
        return True

    def set_shield_mode(self, mode):
        self.shield_policy = mode
        self.aas_enabled = mode == "Auto"
        if mode == "Auto":
            self.add_message("Shield Control", "AAS enabled")
        elif mode == "Manual":
            self.shields_up = True
            self.add_message("Shield Control", "manual shield control")
        elif mode == "Battle Entry":
            self.shields_up = True
            self.shield_strength = [750, 750, 750, 750]
            self.add_message("Shield Control", "battle entry shields")
        elif mode == "Maximum":
            self.shields_up = True
            self.shield_strength = [1000, 1000, 1000, 1000]
            self.add_message("Shield Control", "maximum shields raised")
        self._sync_systems()

    def launch_probe(self):
        if self.probe_loaded <= 0:
            if self.probe_storage > 0:
                self.probe_storage -= 1
                self.probe_loaded += 1
                self.add_message("Probe Control", "probe loaded from storage")
            else:
                self.add_message("Probe Control", "no probes available")
                return False
        self.probe_loaded -= 1
        probe_no = len(self.active_probes) + 1
        contact = self.selected_target
        self.active_probes.append({
            "id": probe_no,
            "mode": "Survey" if contact["kind"] == "planet" else "Track",
            "target": contact["id"],
            "x": self.system_x,
            "y": self.system_y,
            "power": 100,
            "detect": contact["kind"].title(),
            "status": "Outbound",
        })
        self.add_message("Probe Control", f"probe {probe_no} launched toward {contact['name']}")
        return True

    def attempt_boarding(self):
        target = self.selected_target
        if target["kind"] not in ("ship", "base"):
            self.add_message("Security", "boarding target invalid")
            return False
        if target.get("shields_up", False):
            self.add_message("Security", "boarding blocked: target shields up")
            return False
        if self.shock_troops < 10:
            self.add_message("Security", "boarding blocked: troops unavailable")
            return False
        self.shock_troops -= 10
        captured = max(1, target.get("prisoners", 1))
        self.prisoners += captured
        target["prisoners"] = 0
        self.add_message("Security", f"boarding complete: {captured} prisoners held")
        return True

    def target_next_contact(self):
        self.target_index = (self.target_index + 1) % len(self.contacts)
        self.add_message("Targeting", f"target {self.selected_target['name']}")
        self._sync_navigation()

    def add_message(self, source, body):
        item = (str(source)[:16], str(body)[:42])
        if not self.messages or self.messages[-1] != item:
            self.messages.append(item)
            self.messages = self.messages[-9:]

    def report_rows(self):
        dynamic = [
            ("NAV", f"reg {self.nav_region[0]},{self.nav_region[1]} orb {self.nav_orbit[0]}{self.nav_orbit[1]}"),
            ("ENG", f"power {self.energy_pct}% usage {self.energy_usage}%"),
            ("CMB", f"{self.selected_weapon} torps {self.torpedoes}"),
            ("SCI", f"L:{self.probe_loaded} S:{self.probe_storage} contacts {len(self.scanner_contacts())}"),
            ("SEC", f"troops {self.shock_troops} prisoners {self.prisoners}"),
        ]
        return (self.reports + dynamic)[-9:]

    def scanner_contacts(self):
        if self.ecm_enabled:
            return []
        contacts = []
        for contact in self.contacts:
            d = self._distance_to(contact)
            if d <= 18:
                row = dict(contact)
                row["distance"] = d
                contacts.append(row)
        return contacts

    def tactical_contacts(self):
        rows = []
        for contact in self.contacts:
            d = self._distance_to(contact)
            if d <= 25 or contact is self.selected_target:
                row = dict(contact)
                row["distance"] = d
                rows.append(row)
        return rows

    def status_indicator_goods(self):
        return [
            self.energy_pct >= 25,
            self.supplies >= 250,
            self.time_left_days >= 1,
            self.medical_cases == 0,
            self.alert_status != "Red",
            not self.status_flags.get("Mines", False),
            not self.status_flags.get("Distress", False),
            self.hull_pct >= 40,
            not self.ecm_enabled,
            self.shield_pct >= 25,
        ]

    def _move_ship(self, dt):
        if self.rest_mode:
            return
        speed = self.space_velocity * 0.55 + self.hyper_velocity * 0.22
        if speed <= 0:
            return
        angle = math.radians(self.actual_heading - 90)
        self.system_x += math.cos(angle) * speed * dt
        self.system_y += math.sin(angle) * speed * dt
        while self.system_x < 0:
            self.system_x += 50
            self.region_x -= 1
        while self.system_x >= 50:
            self.system_x -= 50
            self.region_x += 1
        while self.system_y < 0:
            self.system_y += 50
            self.region_y -= 1
        while self.system_y >= 50:
            self.system_y -= 50
            self.region_y += 1

    def _drain_energy(self, dt):
        drain = self.energy_usage * dt * (0.08 if not self.rest_mode else 0.03)
        self.energy_units = max(0.0, self.energy_units - drain)
        if self.energy_units <= 0:
            self.hyper_velocity = 0
            self.space_velocity = 0
            self.shields_up = False

    def _reload_weapons(self, dt):
        self.weapon_reload = [max(0.0, r - dt) for r in self.weapon_reload]

    def _advance_clock(self, dt):
        rate = 0.0025 if self.rest_mode else 0.001
        if self.hyper_velocity:
            rate += self.hyper_velocity * 0.0004
        self.mission_elapsed_days += dt * rate
        self.time_left_days = max(0.0, self.time_left_days - dt * rate)

    def _update_probe_tracks(self, dt):
        for probe in self.active_probes:
            contact = next((c for c in self.contacts if c["id"] == probe["target"]), None)
            if contact:
                dx = contact["x"] - probe["x"]
                dy = contact["y"] - probe["y"]
                dist = max(0.01, math.hypot(dx, dy))
                step = min(dist, dt * 3.0)
                probe["x"] += dx / dist * step
                probe["y"] += dy / dist * step
                probe["status"] = "Mapping" if dist < 0.8 else "Outbound"
            probe["power"] = max(0, probe["power"] - dt * 0.35)

    def _sync_systems(self):
        threat_contacts = [c for c in self.scanner_contacts() if c.get("threat")]
        mines = any(c["kind"] == "mine" for c in threat_contacts)
        if self.aas_enabled:
            if threat_contacts:
                self.shields_up = True
                if self.shield_policy == "Auto":
                    self.shield_strength = [850, 850, 850, 850]
            elif self.shield_policy == "Auto":
                self.shields_up = False
        shield_load = 18 if self.shields_up else 0
        if self.shield_policy == "Maximum":
            shield_load = 30
        elif self.shield_policy == "Battle Entry":
            shield_load = 24
        self.energy_usage = max(0, min(100, 20 + self.hyper_velocity * 5 +
                                       self.space_velocity * 3 + shield_load +
                                       (8 if self.tractor_enabled else 0) +
                                       (5 if self.ecm_enabled else 0)))
        self.alert_status = "Red" if threat_contacts and self.shields_up else (
            "Yellow" if threat_contacts or self.energy_pct < 25 or self.hull_pct < 40 else "Green")
        self.status_flags = {
            "LowPwr": self.energy_pct < 25,
            "LowSup": self.supplies < 250,
            "LowTime": self.time_left_days < 1.0,
            "Medical": self.medical_cases > 0,
            "SecAlt": self.alert_status == "Red",
            "Mines": mines,
            "Distress": self.hull_pct < 25 or self.energy_pct < 10,
            "HullPn": self.hull_pct < 40,
        }

    def _sync_navigation(self):
        evasive_offset = 0.0
        if self.nav_evasive:
            evasive_offset = math.sin(self._evasive_phase * 5.0) * 45.0
        slip_offset = 45.0 if self.nav_sideslip > 0 else (-45.0 if self.nav_sideslip < 0 else 0.0)
        self.actual_heading = (self.set_course + slip_offset + evasive_offset) % 360

        target = self.selected_target
        self.nav_region = (round(self.region_x), round(self.region_y))
        orbit_code = chr(ord("A") + max(0, min(25, int(self.system_x // 2))))
        self.nav_orbit = (orbit_code, max(0, min(99, round(self.system_y))))
        self.nav_course = round(self.set_course) % 360
        self.nav_target = (round(target["x"]), round(target["y"]))
        self.nav_distance = round(self._distance_to(target) / 5.0, 1)
        self.nav_object = target["name"] if target["kind"] != "ship" else "Ship"
        if self.docked:
            self.nav_mode = "Docked"
        elif self.in_orbit:
            self.nav_mode = "In Orbit"
        elif self.nav_evasive:
            self.nav_mode = "Evasive"
        elif self.nav_sideslip:
            self.nav_mode = "Sideslip"
        else:
            self.nav_mode = "Underway"

    def _distance_to(self, contact):
        return math.hypot(self.system_x - contact["x"], self.system_y - contact["y"])
