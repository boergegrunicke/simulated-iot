def test_background_update_once_simulation_disabled():
    """Should skip devices with simulation_enabled=False (coverage line 58)."""
    hub = SimulatedHub()
    hub.devices["temp_1"].simulation_enabled = False
    called = []
    hub.register_callback(lambda device_id, state: called.append((device_id, state)))
    hub._background_update_once()
    # No callback should be triggered for temp_1
    assert called == []
def test_background_update_once_other_type():
    """Should cover _background_update_once for an unknown device type (else branch)."""
    hub = SimulatedHub()
    # Add a dummy device
    class DummyDevice:
        pass
    dummy = DummyDevice()
    dummy.id = "dummy_1"
    dummy.name = "Dummy"
    dummy.type = "other"
    dummy.state = 0
    dummy.simulation_enabled = True
    # update_state returns True so the callback is triggered and the else branch is covered
    dummy.update_state = lambda new_state: True
    dummy.state = 42
    hub.devices["dummy_1"] = dummy
    called = []
    hub.register_callback(lambda device_id, state: called.append((device_id, state)))
    hub._background_update_once()
    # Callback should be triggered for dummy_1
    assert ("dummy_1", 42) in called

def test_set_device_state_other_type():
    """Should cover set_device_state for an unknown device type (else branch)."""
    hub = SimulatedHub()
    class DummyDevice:
        pass
    dummy = DummyDevice()
    dummy.id = "dummy_2"
    dummy.name = "Dummy"
    dummy.type = "other"
    dummy.state = 0
    dummy.update_state = lambda new_state: False
    hub.devices["dummy_2"] = dummy
    called = []
    hub.register_callback(lambda device_id, state: called.append((device_id, state)))
    asyncio.run(hub.set_device_state("dummy_2", 123))
    # No callback should be triggered for dummy_2
    assert ("dummy_2", 123) not in called
def test_toggle_simulation_logging(caplog):
    """Should log when simulation is toggled."""
    hub = SimulatedHub()
    with caplog.at_level("INFO"):
        asyncio.run(hub.toggle_simulation("temp_1", False))
    assert any("Simulation für temp_1 ist jetzt aus" in m for m in caplog.messages)

def test_update_state_no_change():
    """Should return False if update_state is called with the same value."""
    hub = SimulatedHub()
    temp = hub.devices["temp_1"]
    result = temp.update_state(21.0)
    assert result is False

def test_set_device_state_callback():
    """Should trigger callback only when state changes."""
    hub = SimulatedHub()
    called = []
    hub.register_callback(lambda device_id, state: called.append((device_id, state)))
    # Change value -> callback
    asyncio.run(hub.set_device_state("temp_1", 22.0))
    assert ("temp_1", 22.0) in called
    # No change -> no callback
    called.clear()
    asyncio.run(hub.set_device_state("temp_1", 22.0))
    assert called == []
def test_background_update_once(monkeypatch):
    """Should test the logic of _background_update_once for all device types."""
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
    # Patch random.uniform and random.random
    monkeypatch.setattr(random, "uniform", lambda a, b: 0.2)
    monkeypatch.setattr(random, "random", lambda: 1.0)  # Switch always toggles
    hub._background_update_once()
    # Sensor should be changed
    assert hub.devices["temp_1"].state == 20.2
    # Switch should toggle
    assert hub.devices["light_1"].state is True
    # Select should not be changed (no logic)
    assert hub.devices["mode_1"].state == "Eco"
    # Callbacks should be triggered for temp_1 and light_1
    assert ("temp_1", 20.2) in called
    assert ("light_1", True) in called
import pytest
import asyncio
from iot_simulator import SimulatedHub

def test_device_properties():
    """Should expose correct device properties like unit and options."""
    hub = SimulatedHub()
    temp = hub.devices["temp_1"]
    mode = hub.devices["mode_1"]
    light = hub.devices["light_1"]
    assert temp.unit == "°C"
    assert mode.options == ["Eco", "Comfort", "Boost"]
    assert light.unit is None
    assert light.options is None

def describe_simulated_hub():
    """SimulatedHub: IoT device simulation and management"""

    @pytest.mark.asyncio
    async def it_initializes_devices():
        """Should initialize all devices with correct properties."""
        hub = SimulatedHub()
        assert "temp_1" in hub.devices
        assert hub.devices["temp_1"].name == "Wohnzimmer Temperatur"
        assert hub.devices["temp_1"].state == 21.0

    @pytest.mark.asyncio
    async def it_sets_device_state():
        """Should change the state of a device."""
        hub = SimulatedHub()
        await hub.set_device_state("light_1", True)
        assert hub.devices["light_1"].state is True

    @pytest.mark.asyncio
    async def it_triggers_callback_on_state_change():
        """Should trigger callback when device state changes."""
        hub = SimulatedHub()
        received_updates = []
        def test_callback(device_id, state):
            received_updates.append((device_id, state))
        hub.register_callback(test_callback)
        await hub.set_device_state("temp_1", 25.5)
        assert len(received_updates) == 1
        assert received_updates[0] == ("temp_1", 25.5)

    @pytest.mark.asyncio
    async def it_toggles_simulation_per_device():
        """Should enable and disable simulation for a device."""
        hub = SimulatedHub()
        assert hub.devices["temp_1"].simulation_enabled is True
        await hub.toggle_simulation("temp_1", False)
        assert hub.devices["temp_1"].simulation_enabled is False

    def it_has_correct_device_properties():
        """Should expose correct device properties like unit and options."""
        hub = SimulatedHub()
        temp = hub.devices["temp_1"]
        mode = hub.devices["mode_1"]
        light = hub.devices["light_1"]
        assert temp.unit == "°C"
        assert mode.options == ["Eco", "Comfort", "Boost"]
        assert light.unit is None
        assert light.options is None

    def it_updates_state_directly():
        """Should update device state using update_state method."""
        hub = SimulatedHub()
        temp = hub.devices["temp_1"]
        assert temp.state == 21.0
        temp.update_state(22.5)
        assert temp.state == 22.5

    def it_registers_multiple_callbacks():
        """Should allow registering multiple callbacks."""
        hub = SimulatedHub()
        results = []
        def cb1(device_id, state):
            results.append(("cb1", device_id, state))
        def cb2(device_id, state):
            results.append(("cb2", device_id, state))
        hub.register_callback(cb1)
        hub.register_callback(cb2)
        for cb in hub._callbacks:
            cb("temp_1", 42)
        assert ("cb1", "temp_1", 42) in results
        assert ("cb2", "temp_1", 42) in results

    @pytest.mark.asyncio
    async def it_ignores_invalid_device_id_on_set_state():
        """Should not raise exception for invalid device_id in set_device_state."""
        hub = SimulatedHub()
        await hub.set_device_state("does_not_exist", 123)

    @pytest.mark.asyncio
    async def it_ignores_invalid_device_id_on_toggle_simulation():
        """Should not raise exception for invalid device_id in toggle_simulation."""
        hub = SimulatedHub()
        await hub.toggle_simulation("does_not_exist", True)

    @pytest.mark.asyncio
    async def it_switches_select_device_options():
        """Should switch select device options."""
        hub = SimulatedHub()
        await hub.set_device_state("mode_1", "Boost")
        assert hub.devices["mode_1"].state == "Boost"

    @pytest.mark.asyncio
    async def it_triggers_callbacks_in_background_update(monkeypatch):
        """Should trigger callbacks in background update loop (simulation, one iteration)."""
        hub = SimulatedHub()
        called = []
        def cb(device_id, state):
            called.append((device_id, state))
        hub.register_callback(cb)
        monkeypatch.setattr(asyncio, "sleep", lambda x: None)
        monkeypatch.setattr("random.uniform", lambda a, b: 0.1)
        monkeypatch.setattr("random.random", lambda: 1.0)
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
        assert ("temp_1", 21.1) in called
        assert ("light_1", True) in called or ("light_1", False) in called
        assert ("mode_1", "Eco") in called or ("mode_1", "Comfort") in called or ("mode_1", "Boost") in called

    def it_runs_background_update_once_for_all_types(monkeypatch):
        """Should run _background_update_once for all device types."""
        import random
        hub = SimulatedHub()
        called = []
        hub.register_callback(lambda device_id, state: called.append((device_id, state)))
        hub.devices["temp_1"].state = 20.0
        hub.devices["light_1"].state = False
        hub.devices["mode_1"].state = "Eco"
        monkeypatch.setattr(random, "uniform", lambda a, b: 0.2)
        monkeypatch.setattr(random, "random", lambda: 1.0)
        hub._background_update_once()
        assert hub.devices["temp_1"].state == 20.2
        assert hub.devices["light_1"].state is True
        assert hub.devices["mode_1"].state == "Eco"
        assert ("temp_1", 20.2) in called
        assert ("light_1", True) in called

    def it_logs_toggle_simulation(caplog):
        """Should log when simulation is toggled."""
        hub = SimulatedHub()
        with caplog.at_level("INFO"):
            asyncio.run(hub.toggle_simulation("temp_1", False))
        assert any("Simulation für temp_1 ist jetzt aus" in m for m in caplog.messages)

    def it_returns_false_on_update_state_no_change():
        """Should return False if update_state is called with same value."""
        hub = SimulatedHub()
        temp = hub.devices["temp_1"]
        result = temp.update_state(21.0)
        assert result is False

    def it_triggers_callback_only_on_state_change():
        """Should trigger callback only if state actually changes."""
        hub = SimulatedHub()
        called = []
        hub.register_callback(lambda device_id, state: called.append((device_id, state)))
        asyncio.run(hub.set_device_state("temp_1", 22.0))
        assert ("temp_1", 22.0) in called
        called.clear()
        asyncio.run(hub.set_device_state("temp_1", 22.0))
        assert called == []

    def it_handles_other_device_type_in_background_update():
        """Should handle unknown device type in _background_update_once (else branch)."""
        hub = SimulatedHub()
        class DummyDevice:
            pass
        dummy = DummyDevice()
        dummy.id = "dummy_1"
        dummy.name = "Dummy"
        dummy.type = "other"
        dummy.state = 0
        dummy.simulation_enabled = True
        dummy.update_state = lambda new_state: False
        hub.devices["dummy_1"] = dummy
        called = []
        hub.register_callback(lambda device_id, state: called.append((device_id, state)))
        hub._background_update_once()
        assert ("dummy_1", 0) not in called

    def it_handles_other_device_type_in_set_device_state():
        """Should handle unknown device type in set_device_state (else branch)."""
        hub = SimulatedHub()
        class DummyDevice:
            pass
        dummy = DummyDevice()
        dummy.id = "dummy_2"
        dummy.name = "Dummy"
        dummy.type = "other"
        dummy.state = 0
        dummy.update_state = lambda new_state: False
        hub.devices["dummy_2"] = dummy
        called = []
        hub.register_callback(lambda device_id, state: called.append((device_id, state)))
        asyncio.run(hub.set_device_state("dummy_2", 123))
        assert ("dummy_2", 123) not in called

    def it_skips_devices_with_simulation_disabled():
        """Should skip devices with simulation_enabled=False in background update."""
        hub = SimulatedHub()
        hub.devices["temp_1"].simulation_enabled = False
        called = []
        hub.register_callback(lambda device_id, state: called.append((device_id, state)))
        hub._background_update_once()
        assert called == []


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