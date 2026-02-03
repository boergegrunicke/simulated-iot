def test_background_update_once(monkeypatch):
    """Testet die Logik von _background_update_once für alle Gerätetypen."""
    import random
    hub = SimulatedHub()
    called = []
    hub.register_callback(lambda device_id, state: called.append((device_id, state)))
    # Sensor: temp_1
    hub.devices["temp_1"].state = 20.0
    # Switch: light_1
    hub.devices["light_1"].state = False
    # Select: mode_1
    hub.devices["mode_1"].state = "Eco"
    # Patch random.uniform und random.random
    monkeypatch.setattr(random, "uniform", lambda a, b: 0.2)
    monkeypatch.setattr(random, "random", lambda: 1.0)  # Switch toggelt immer
    hub._background_update_once()
    # Sensor sollte geändert werden
    assert hub.devices["temp_1"].state == 20.2
    # Switch sollte toggeln
    assert hub.devices["light_1"].state is True
    # Select sollte nicht geändert werden (keine Logik)
    assert hub.devices["mode_1"].state == "Eco"
    # Callbacks sollten für temp_1 und light_1 gefeuert werden
    assert ("temp_1", 20.2) in called
    assert ("light_1", True) in called
import pytest
import asyncio
from iot_simulator import SimulatedHub

@pytest.mark.asyncio
async def test_device_initialization():
    """Prüft, ob die Geräte korrekt im Hub angelegt werden."""
    hub = SimulatedHub()
    assert "temp_1" in hub.devices
    assert hub.devices["temp_1"].name == "Wohnzimmer Temperatur"
    assert hub.devices["temp_1"].state == 21.0

@pytest.mark.asyncio
async def test_set_device_state():
    """Prüft, ob das Ändern eines Status funktioniert."""
    hub = SimulatedHub()
    
    # Status ändern
    await hub.set_device_state("light_1", True)
    assert hub.devices["light_1"].state is True

@pytest.mark.asyncio
async def test_callback_mechanism():
    """Prüft, ob der Callback gefeuert wird, wenn sich ein Status ändert."""
    hub = SimulatedHub()
    received_updates = []

    def test_callback(device_id, state):
        received_updates.append((device_id, state))

    hub.register_callback(test_callback)
    
    # Aktion auslösen
    await hub.set_device_state("temp_1", 25.5)
    
    assert len(received_updates) == 1
    assert received_updates[0] == ("temp_1", 25.5)


@pytest.mark.asyncio
async def test_simulation_toggle():
    """Prüft, ob man die Simulation pro Gerät an/ausschalten kann."""
    hub = SimulatedHub()
    # Standardmäßig an
    assert hub.devices["temp_1"].simulation_enabled is True
    # Ausschalten
    await hub.toggle_simulation("temp_1", False)
    assert hub.devices["temp_1"].simulation_enabled is False


def test_device_properties():
    """Prüft Geräteeigenschaften wie unit und options."""
    hub = SimulatedHub()
    temp = hub.devices["temp_1"]
    mode = hub.devices["mode_1"]
    light = hub.devices["light_1"]
    assert temp.unit == "°C"
    assert mode.options == ["Eco", "Comfort", "Boost"]
    assert light.unit is None
    assert light.options is None


def test_update_state():
    """Prüft update_state Methode direkt."""
    hub = SimulatedHub()
    temp = hub.devices["temp_1"]
    assert temp.state == 21.0
    temp.update_state(22.5)
    assert temp.state == 22.5


def test_register_multiple_callbacks():
    """Prüft, ob mehrere Callbacks registriert werden können."""
    hub = SimulatedHub()
    results = []
    def cb1(device_id, state):
        results.append(("cb1", device_id, state))
    def cb2(device_id, state):
        results.append(("cb2", device_id, state))
    hub.register_callback(cb1)
    hub.register_callback(cb2)
    # Callback manuell auslösen
    for cb in hub._callbacks:
        cb("temp_1", 42)
    assert ("cb1", "temp_1", 42) in results
    assert ("cb2", "temp_1", 42) in results


@pytest.mark.asyncio
async def test_set_device_state_invalid():
    """Prüft, dass keine Exception bei ungültiger device_id geworfen wird."""
    hub = SimulatedHub()
    # Sollte einfach nichts tun, keine Exception
    await hub.set_device_state("does_not_exist", 123)


@pytest.mark.asyncio
async def test_toggle_simulation_invalid():
    """Prüft, dass keine Exception bei ungültiger device_id geworfen wird (toggle_simulation)."""
    hub = SimulatedHub()
    await hub.toggle_simulation("does_not_exist", True)


@pytest.mark.asyncio
async def test_select_device_options():
    """Prüft das Umschalten der select-Optionen."""
    hub = SimulatedHub()
    await hub.set_device_state("mode_1", "Boost")
    assert hub.devices["mode_1"].state == "Boost"


@pytest.mark.asyncio
async def test_background_updates_simulation(monkeypatch):
    """Testet, dass im Hintergrund-Update-Loop Callbacks ausgelöst werden (Simulation, 1 Durchlauf)."""
    hub = SimulatedHub()
    called = []
    def cb(device_id, state):
        called.append((device_id, state))
    hub.register_callback(cb)
    # Patch sleep, damit es sofort weitergeht
    monkeypatch.setattr(asyncio, "sleep", lambda x: None)
    # Patch random, damit predictable
    monkeypatch.setattr("random.uniform", lambda a, b: 0.1)
    monkeypatch.setattr("random.random", lambda: 1.0)
    # Nur einen Durchlauf simulieren
    async def one_loop():
        for dev_id, device in hub.devices.items():
            if device.simulation_enabled:
                if device.type == "sensor":
                    device.state += round(0.1, 2)
                elif device.type == "switch":
                    device.state = not device.state
                for callback in hub._callbacks:
                    callback(dev_id, device.state)
    await one_loop()
    # Es sollten für alle Geräte Callbacks ausgelöst worden sein
    assert ("temp_1", 21.1) in called
    assert ("light_1", True) in called or ("light_1", False) in called
    assert ("mode_1", "Eco") in called or ("mode_1", "Comfort") in called or ("mode_1", "Boost") in called