# pigeon-deterrent-iot

=== Flood Detection & Camera Control - Run Instructions ===

1. Install required Python packages:
   `pip install gpiozero paho-mqtt`

2. Start Mosquitto MQTT Broker (if you have it installed):
   - For Mac users with Homebrew:
     `brew services start mosquitto`
   - For Linux users:
     `sudo systemctl start mosquitto`

3. Run the main Python script:
   `python pigeon_detect_simulation.py`

4. Open a new terminal to subscribe to the MQTT topic:
   `mosquitto_sub -h 127.0.0.1 -p 1883 -t house/camera`

5. To manually control the camera via MQTT, publish these commands:
   - Open the camera:
     `mosquitto_pub -h 127.0.0.1 -p 1883 -t house/camera -m "OPEN"`

   - Close the camera (disable motion-triggered camera):
     `mosquitto_pub -h 127.0.0.1 -p 1883 -t house/camera -m "CLOSE"`

   - Return to automatic motion detection mode:
     `mosquitto_pub -h 127.0.0.1 -p 1883 -t house/camera -m "AUTO"`

=== Notes ===
- Make sure the Mosquitto MQTT broker is running before starting the project.
- Ensure 'camera_detect.py' exists in the same directory as 'pigeon_detect_simulation.py'.
- Python 3.x is required for gpiozero and paho-mqtt to work properly.

`mosquitto -c mosquitto.conf`