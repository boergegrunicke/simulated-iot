# simulated-iot
Tiny simulator, that is inteded to simulate iot devices for testing purposes in an async style.

![Tests](https://github.com/boergegrunicke/simulated-iot/actions/workflows/python-tests.yml/badge.svg)

## Overview

This library provides a simple, asynchronous simulation of IoT devices. It is especially useful for testing and development when no real hardware is available.

### Main Features

- **Simulated Devices:**
	- Sensors (e.g., temperature)
	- Switches (e.g., lights)
	- Select devices (e.g., heating mode)
- **Asynchronous State Changes:**
	- Devices periodically simulate state changes (e.g., temperature fluctuations, random toggling of switches).
- **Callbacks:**
	- State changes are reported via callback functions.
- **Controllable Simulation:**
	- Simulation can be enabled or disabled per device.
- **Manual Control:**
	- States can also be set manually, which also triggers callbacks.

### Example Devices

- `Living Room Temperature` (sensor, °C)
- `Ceiling Light` (switch)
- `Heating Mode` (select: Eco, Comfort, Boost)

For more details and the API, see the module `iot_simulator/hub.py`.