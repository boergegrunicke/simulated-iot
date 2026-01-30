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
        """Der Loop, der zufällig Werte ändert, wenn die Simulation aktiv ist."""
        while True:
            await asyncio.sleep(5) # Alle 5 Sekunden prüfen
            for dev_id, device in self.devices.items():
                if device.simulation_enabled:
                    # Zufallslogik
                    if device.type == "sensor":
                        device.state += round(random.uniform(-0.2, 0.2), 2)
                    elif device.type == "switch":
                        # Nur selten umschalten, damit es nicht nervt
                        if random.random() > 0.9: 
                            device.state = not device.state
                    
                    # Benachrichtige Home Assistant über das Update
                    for callback in self._callbacks:
                        callback(dev_id, device.state)

    async def set_device_state(self, device_id, new_state):
        if device_id in self.devices:
            self.devices[device_id].update_state(new_state)
            # Auch bei manueller Änderung Callback feuern
            for callback in self._callbacks:
                callback(device_id, new_state)