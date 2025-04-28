from gpiozero import LED, Buzzer, MotionSensor  # type: ignore
from time import sleep
import subprocess
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# Setup GPIO pins
led = LED(22)
buzzer = Buzzer(16)
motion_sensor = MotionSensor(27)

# Camera control flags
camera_enabled = True  # Normally enable motion detection
manual_open = False    # Normally no manual camera open yet
camera_process = None  # To store the camera subprocess

# ---------------- MQTT CONFIG ----------------
BROKER = "127.0.0.1"
PORT = 1883
USERNAME = "pk"
PASSWORD = "iot1234"
TOPIC_SUB = "house/camera"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[MQTT] Connected with result code {reason_code}")
    client.subscribe(TOPIC_SUB)

def on_message(client, userdata, msg):
    global manual_open, camera_enabled, camera_process

    print(f"[MQTT] {msg.topic}: {msg.payload}")
    msg_str = msg.payload.decode("utf-8").strip().upper()

    if msg_str == 'OPEN':
        print("[ACTION] Manual OPEN camera now!")
        manual_open = True

    elif msg_str == 'CLOSE':
        print("[ACTION] Turn OFF camera trigger and terminate camera process")
        camera_enabled = False
        if camera_process and camera_process.poll() is None:  # If the process is still running
            print("[ACTION] Terminating camera process...")
            camera_process.terminate()
            camera_process = None

    elif msg_str == 'AUTO':
        print("[ACTION] Turn ON motion detection mode")
        camera_enabled = True

client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT, 60)
client.loop_start()

# ---------------- MAIN PROGRAM ----------------
def on_motion():
    global camera_enabled, camera_process
    if camera_enabled:
        print("Motion detected! Launching subprocess to open the camera...")
        camera_process = subprocess.Popen(["python3", "camera_detect.py"])
    else:
        print("[MOTION] Detected, but camera trigger disabled.")

def main():
    global manual_open, camera_process
    motion_sensor.when_motion = on_motion

    while True:
        if manual_open:
            print("[MANUAL] Open the camera via MQTT command...")
            camera_process = subprocess.Popen(["python3", "camera_detect.py"])
            manual_open = False

        print("System is running, waiting for motion detection...")
        sleep(0.5)

if __name__ == "__main__":
    main()
