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


if __name__ == "__main__":
    unittest.main()
