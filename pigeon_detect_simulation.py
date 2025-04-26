from tkgpio import TkCircuit

configuration = {
    "name": "My Big Project",
    "width": 700,
    "height": 550,
    "leds": [
        {
            "x": 400,
            "y": 110,
            "name": "LED 2",
            "pin": 22
        }
    ],
    "buzzers": [
        {
            "x": 50,
            "y": 170,
            "name": "Buzzer",
            "pin": 16,
            "frequency": 440
        }
    ],
    "motion_sensors": [
        {
            "x": 150,
            "y": 170,
            "name": "Motion Sensor",
            "pin": 27,
            "detection_radius": 50,
            "delay_duration": 5,
            "block_duration": 3
        }
    ]
}

circuit = TkCircuit(configuration)

@circuit.run
def main():
    import pigeon_detect

    pigeon_detect.main()