import unittest

from state import ShipState


class GameplayStateTests(unittest.TestCase):
    def test_engine_tick_moves_ship_and_drains_energy(self):
        state = ShipState()
        start = (state.system_x, state.system_y, state.energy_units)
        state.change_space_velocity(3)
        state.tick(1.0)
        self.assertNotEqual((state.system_x, state.system_y), start[:2])
        self.assertLess(state.energy_units, start[2])
        self.assertGreater(state.energy_usage, 20)

    def test_sideslip_changes_actual_heading_not_set_course(self):
        state = ShipState()
        course = state.nav_course
        state.adjust_nav_sideslip(1)
        state.tick(0.1)
        self.assertEqual(state.nav_course, course)
        self.assertEqual(round((state.actual_heading - course) % 360), 45)

    def test_aas_and_ecm_follow_manual_sensor_rules(self):
        state = ShipState()
        self.assertTrue(any(c["threat"] for c in state.scanner_contacts()))
        state.set_shield_mode("Auto")
        state.tick(0.1)
        self.assertTrue(state.aas_enabled)
        self.assertTrue(state.shields_up)
        self.assertEqual(state.alert_status, "Red")
        state.toggle_ecm(True)
        self.assertEqual(state.scanner_contacts(), [])
        self.assertGreaterEqual(len(state.tactical_contacts()), 1)

    def test_weapon_fire_consumes_torpedo_and_reloads(self):
        state = ShipState()
        state.select_weapon("Trp1")
        torps = state.torpedoes
        self.assertTrue(state.fire_selected_weapon())
        self.assertEqual(state.torpedoes, torps - 1)
        self.assertGreater(state.weapon_reload[state.weapon_index], 0)

    def test_probe_launch_and_boarding_gate(self):
        state = ShipState()
        loaded = state.probe_loaded
        self.assertTrue(state.launch_probe())
        self.assertEqual(state.probe_loaded, loaded - 1)
        self.assertEqual(len(state.active_probes), 1)

        enemy = next(i for i, c in enumerate(state.contacts) if c.kind == "ship")
        state.target_index = enemy
        state.contacts[enemy].shields_up = True
        self.assertFalse(state.attempt_boarding())
        state.contacts[enemy].shields_up = False
        prisoners = state.prisoners
        self.assertTrue(state.attempt_boarding())
        self.assertGreater(state.prisoners, prisoners)

    def test_boarding_context_for_valid_blocked_and_invalid_targets(self):
        state = ShipState()
        enemy = next(i for i, c in enumerate(state.contacts) if c.kind == "ship")
        state.target_index = enemy
        state.contacts[enemy].shields_up = True
        ctx = state.boarding_context()
        self.assertTrue(ctx["valid"])
        self.assertTrue(ctx["shields_up"])
        self.assertIn("SHIELDS", ctx["status"])
        self.assertGreater(ctx["defenders"], 0)
        self.assertGreater(len(ctx["compartments"]), 0)

        state.contacts[enemy].shields_up = False
        ctx = state.boarding_context()
        self.assertTrue(ctx["valid"])
        self.assertFalse(ctx["shields_up"])
        self.assertEqual(ctx["status"], "READY TO BOARD")

        planet = next(i for i, c in enumerate(state.contacts) if c.kind == "planet")
        state.target_index = planet
        ctx = state.boarding_context()
        self.assertFalse(ctx["valid"])
        self.assertEqual(ctx["status"], "NO BOARDING TARGET")

    def test_successful_boarding_updates_context(self):
        state = ShipState()
        enemy = next(i for i, c in enumerate(state.contacts) if c.kind == "ship")
        state.target_index = enemy
        state.contacts[enemy].shields_up = False
        troops = state.shock_troops
        defenders = state.contacts[enemy].defenders
        self.assertTrue(state.attempt_boarding())
        ctx = state.boarding_context()
        self.assertLess(state.shock_troops, troops)
        self.assertLess(ctx["defenders"], defenders)
        self.assertIn(ctx["status"], ("Boarding action underway", "Secured"))


if __name__ == "__main__":
    unittest.main()
