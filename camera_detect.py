import torch  # type: ignore
import cv2  # type: ignore
from pathlib import Path
import paho.mqtt.client as mqtt 
from paho.mqtt.enums import CallbackAPIVersion 

# Set paths
current_dir = Path(__file__).parent
local_repo = current_dir / 'yolov5'  # yolov5 folder (cloned repository)
model_path = local_repo / 'yolov5s.pt'  # path to the yolov5s.pt weights file

model = torch.hub.load(str(local_repo), 'custom', path=str(model_path), source='local')
animal_classes = ['cat', 'dog', 'bird', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']

def main():
    # === Create MQTT client first ===
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.username_pw_set('pk', 'iot1234')
    client.connect('127.0.0.1', 1883, 60)
    client.loop_start()  # Non-blocking

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open the camera")
        return

    checking_bird = False
    bird_confirm_count = 0
    bird_confirm_target = 30  # Number of consecutive frames required to confirm bird detection

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Cannot read frame")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(frame_rgb)

        found_bird = False

        for *box, conf, cls in results.xyxy[0]:
            label = model.names[int(cls)]
            if label in animal_classes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                if label == 'bird':
                    found_bird = True
                    break  
                
        if not checking_bird and found_bird:
            print("First detection of 'bird'. Starting confirmation process...")
            checking_bird = True
            bird_confirm_count = 0

        if checking_bird:
            if found_bird:
                bird_confirm_count += 1
            else:
                bird_confirm_count = 0 

            if bird_confirm_count >= bird_confirm_target:
                print("\n✅ Confirmed: 'Bird' detected continuously for 30 frames. Closing the camera!")
                client.publish('house/bird', 'BIRD_CONFIRMED')  # Now client exists here
                break

        cv2.imshow('Pigeon Detect', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
