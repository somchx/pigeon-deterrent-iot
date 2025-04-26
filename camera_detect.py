import torch
import cv2
from pathlib import Path

# Set path
current_dir = Path(__file__).parent
local_repo = current_dir / 'yolov5'  # โฟลเดอร์ yolov5 ที่ clone ไว้
model_path = local_repo / 'yolov5s.pt'  # path ไปที่ไฟล์ weights yolov5s.pt

# โหลดโมเดล
model = torch.hub.load(str(local_repo), 'custom', path=str(model_path), source='local')

# animal classes ที่ต้องการ
animal_classes = ['cat', 'dog', 'bird', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ไม่สามารถเปิดกล้องได้")
        return

    checking_bird = False
    bird_confirm_count = 0
    bird_confirm_target = 30  # จำนวนครั้งที่ต้องตรวจสอบ bird ต่อเนื่อง

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ไม่สามารถอ่านเฟรมได้")
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
            print("ตรวจพบ 'นก' ครั้งแรก เริ่มกระบวนการยืนยัน...")
            checking_bird = True
            bird_confirm_count = 0

        if checking_bird:
            if found_bird:
                bird_confirm_count += 1
            else:
                bird_confirm_count = 0 

            if bird_confirm_count >= bird_confirm_target:
                print("\n✅ ยืนยันแล้ว: พบ 'นก' ต่อเนื่องครบ 30 ครั้ง ปิดกล้อง!")
                break

        cv2.imshow('Pigeon Detect', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
