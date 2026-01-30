import asyncio
import random
import logging

_LOGGER = logging.getLogger(__name__)

class SimulatedDevice:
    def __init__(self, device_id, name, device_type, initial_state):
        self.id = device_id
        self.name = name
        self.type = device_type
        self.state = initial_state
        # Hier ist die neue Funktion: Simulation pro Gerät an/aus
        self.simulation_enabled = True 
        self.unit = "°C" if device_type == "sensor" else None
        self.options = ["Eco", "Comfort", "Boost"] if device_type == "select" else None

    def update_state(self, new_state):
        if self.state == new_state:
            return False  # No change, do not update
        self.state = new_state
        return True

class SimulatedHub:
    def __init__(self):
        # Wir erstellen eine Liste von Test-Geräten
        self.devices = {
            "temp_1": SimulatedDevice("temp_1", "Wohnzimmer Temperatur", "sensor", 21.0),
            "light_1": SimulatedDevice("light_1", "Deckenlicht", "switch", False),
            "mode_1": SimulatedDevice("mode_1", "Heizungsmodus", "select", "Eco"),
        }
        self._callbacks = set()

    def register_callback(self, callback):
        self._callbacks.add(callback)

    async def toggle_simulation(self, device_id, enable: bool):
        if device_id in self.devices:
            self.devices[device_id].simulation_enabled = enable
            _LOGGER.info(f"Simulation für {device_id} ist jetzt {'an' if enable else 'aus'}")

    async def start_background_updates(self):
        """Loop that randomly changes values if simulation is active."""
        while True:
            await asyncio.sleep(5) # Check every 5 seconds
            for dev_id, device in self.devices.items():
                if device.simulation_enabled:
                    old_state = device.state
                    # Random logic
                    if device.type == "sensor":
                        # Ensure new value is different
                        delta = round(random.uniform(-0.2, 0.2), 2)
                        new_state = round(old_state + delta, 2)
                        if new_state == old_state:
                            # Force a minimal change if random gave 0
                            new_state = round(old_state + (0.2 if delta <= 0 else -0.2), 2)
                        changed = device.update_state(new_state)
                    elif device.type == "switch":
                        if random.random() > 0.9:
                            new_state = not old_state
                            changed = device.update_state(new_state)
                        else:
                            changed = False
                    else:
                        changed = False
                    # Only fire callback if state actually changed
                    if changed:
                        for callback in self._callbacks:
                            callback(dev_id, device.state)

    async def set_device_state(self, device_id, new_state):
        if device_id in self.devices:
            changed = self.devices[device_id].update_state(new_state)
            # Only fire callback if state actually changed
            if changed:
                for callback in self._callbacks:
                    callback(device_id, new_state)