from gpiozero import LED, Buzzer, MotionSensor
from time import sleep
import subprocess

led = LED(22)
buzzer = Buzzer(16)
motion_sensor = MotionSensor(27)

def on_motion():
    print("ตรวจจับการเคลื่อนไหวแล้ว! เรียก subprocess เปิดกล้อง...")
    subprocess.run(["python3", "camera_detect.py"])

def main():
    motion_sensor.when_motion = on_motion

    while True:
        print("ระบบเริ่มทำงาน รอการตรวจจับการเคลื่อนไหว...")
        sleep(0.5)

if __name__ == "__main__":
    main()
