from ultralytics import YOLO
import cv2
import numpy as np
import csv
import os

model = YOLO("yolov8n.pt")
vehicle_classes = [2, 3, 5, 7]

# Define your video sources (rename files accordingly)
CAM_SOURCES = {
    "cam1": "videos/cam1.mp4",
    "cam2": "videos/cam2.mp4",
    "cam3": "videos/cam3.mp4",
    "cam4": "videos/cam4.mp4",  # Optional for 4-way junction
}

# Lane division function (same as before)
def get_lane(frame, lane_id):
    height, width, _ = frame.shape
    if lane_id == 1:
        return (0, int(width / 3))
    elif lane_id == 2:
        return (int(width / 3), int(2 * width / 3))
    elif lane_id == 3:
        return (int(2 * width / 3), width)

# Initialize video capture + CSV for each camera
caps = {}
csv_writers = {}
frame_counts = {}
for cam_id, path in CAM_SOURCES.items():
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"❌ Couldn't open {cam_id}")
        continue
    caps[cam_id] = cap

    log_path = f"logs/counts_{cam_id}.csv"
    if os.path.exists(log_path):
        os.remove(log_path)

    csv_file = open(log_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Frame", "Lane 1", "Lane 2", "Lane 3"])
    csv_writers[cam_id] = (csv_file, csv_writer)
    frame_counts[cam_id] = 0
print("hiii")
# Main loop for all cameras
while any(cap.isOpened() for cap in caps.values()):
    for cam_id, cap in caps.items():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 360))
        results = model(frame)[0]

        lane_counts = {1: 0, 2: 0, 3: 0}
        try:
            classes = results.boxes.cls.cpu().numpy()
            cords = results.boxes.xyxy.cpu().numpy()
        except:
            continue

        for cls_id, (x1, y1, x2, y2) in zip(classes, cords):
            if int(cls_id) in vehicle_classes:
                x_center = (x1 + x2) / 2
                for lane_id in lane_counts:
                    lane_start, lane_end = get_lane(frame, lane_id)
                    if lane_start <= x_center <= lane_end:
                        lane_counts[lane_id] += 1
                        break
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        height, width, _ = frame.shape
        cv2.line(frame, (int(width / 3), 0), (int(width / 3), height), (255, 0, 0), 2)
        cv2.line(frame, (int(2 * width / 3), 0), (int(2 * width / 3), height), (255, 0, 0), 2)

        # Write to CSV
        csv_file, writer = csv_writers[cam_id]
        writer.writerow([
            frame_counts[cam_id],
            lane_counts[1], lane_counts[2], lane_counts[3]
        ])
        frame_counts[cam_id] += 1

        # Show live detection for that camera
        cv2.imshow(f"Camera: {cam_id}", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
for cap in caps.values():
    cap.release()
for cam_id in csv_writers:
    csv_writers[cam_id][0].close()
cv2.destroyAllWindows()
print("✅ Vehicle counting finished for all cameras.")
