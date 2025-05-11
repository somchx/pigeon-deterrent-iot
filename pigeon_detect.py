from gpiozero import LED, Buzzer, MotionSensor  # type: ignore
from time import sleep
import subprocess
import paho.mqtt.client as mqtt # type: ignore
from paho.mqtt.enums import CallbackAPIVersion # type: ignore

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
    client.subscribe("house/camera")
    client.subscribe("house/bird")  # <== Subscribe new topic

def on_message(client, userdata, msg):
    global manual_open, camera_enabled, camera_process

    print(f"[MQTT] {msg.topic}: {msg.payload}")
    msg_str = msg.payload.decode("utf-8").strip().upper()

    if msg.topic == 'house/camera':
        if msg_str == 'OPEN':
            print("[ACTION] Manual OPEN camera now!")
            manual_open = True
        elif msg_str == 'CLOSE':
            print("[ACTION] Turn OFF camera trigger and terminate camera process")
            camera_enabled = False
            if camera_process and camera_process.poll() is None:
                print("[ACTION] Terminating camera process...")
                camera_process.terminate()
                camera_process = None
        elif msg_str == 'AUTO':
            print("[ACTION] Turn ON motion detection mode")
            camera_enabled = True

    elif msg.topic == 'house/bird':
        if msg_str == 'BIRD_CONFIRMED':
            print("[BUZZER] Bird confirmed detected! Activating buzzer...")
            buzzer.on()
            sleep(15)  # Buzzer on 2 seconds
            buzzer.off()

client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT, 60)
client.loop_start()

# ---------------- MAIN PROGRAM ----------------
def on_motion():
    global camera_enabled, camera_process
    print("[MOTION] Detected.")
    led.on()

    if camera_enabled:
        if not camera_process or camera_process.poll() is not None:
            print("Launching camera subprocess...")
            camera_process = subprocess.Popen(["python3", "camera_detect.py"])
        else:
            print("Camera already running. Skipping new launch.")
    else:
        print("[MOTION] Detected, but camera trigger disabled.")

def on_no_motion():
    print("[MOTION] Stopped.")
    led.off()

def main():
    global manual_open, camera_process

    motion_sensor.when_motion = on_motion
    motion_sensor.when_no_motion = on_no_motion

    while True:
        if manual_open:
            if not camera_process or camera_process.poll() is not None:
                print("[MANUAL] Open the camera via MQTT command...")
                camera_process = subprocess.Popen(["python3", "camera_detect.py"])
            else:
                print("[MANUAL] Camera already running. Skipping new launch.")
            manual_open = False

        print("System is running, waiting for motion detection...")
        sleep(0.5)

if __name__ == "__main__":
    main()
