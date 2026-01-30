import asyncio
from iot_simulator.hub import SimulatedHub

# Example callback function to handle device state updates
def device_update_callback(device_id, new_state):
    print(f"Device '{device_id}' updated state to: {new_state}")

async def main():
    # Create the simulated hub
    hub = SimulatedHub()

    # Print all initial device states
    print("Initial device states:")
    for dev_id, device in hub.devices.items():
        print(f"  {dev_id}: {device.state}")

    # Register the callback to receive updates
    hub.register_callback(device_update_callback)

    # Start the background simulation loop (runs in the background)
    asyncio.create_task(hub.start_background_updates())

    # Example: manually set device states
    await hub.set_device_state("light_1", True)  # Turn on the ceiling light
    await hub.set_device_state("mode_1", "Boost")  # Change heating mode

    # Example: disable simulation for a device
    await hub.toggle_simulation("temp_1", False)

    # Keep the script running to receive updates
    await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(main())
