"""Mutable runtime state for the cockpit, separated from drawing code."""


class ShipState:
    """All values the consoles read and the input layer mutates."""

    def __init__(self):
        # Engineering: hyperspace and normal-space velocity steps (0..10).
        self.hyper_velocity = 0
        self.space_velocity = 0
        self.energy_usage = 20
        # Engineering damage cycle: 1 ok, 2 damaged, 3 heavy, 4 destroyed.
        self.damage_level = 1

        # Combat weapon selection and target board.
        self.weapon_index = 0
        self.weapons = ["Phaser", "Trp1", "Trp2", "ObltrPd"]

        # Communication feed scroll position.
        self.feed_index = 1
        self.feed_clock = 0

    @property
    def energy_color(self):
        if self.energy_usage > 60:
            return "red"
        if self.energy_usage > 25:
            return "yellow"
        return "green"
