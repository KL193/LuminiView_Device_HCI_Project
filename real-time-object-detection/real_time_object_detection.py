import cv2
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import threading
import time
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
import requests

# URLs of the files
weights_url = 'https://pjreddie.com/media/files/yolov3.weights'
cfg_url = 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg'

# Download yolov3.weights
weights_response = requests.get(weights_url)
with open('yolov3.weights', 'wb') as f:
    f.write(weights_response.content)

# Download yolov3.cfg
cfg_response = requests.get(cfg_url)
with open('yolov3.cfg', 'wb') as f:
    f.write(cfg_response.content)

print("Downloaded yolov3.weights and yolov3.cfg successfully.")


# MongoDB connection
client = MongoClient('mongodb+srv://hci_user:oUoaJXKsn2MFCeHU@cluster0.gbt6n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['face_detection_db']
collection = db['detection_status']

# Load YOLOv3 model
print("[INFO] Loading YOLOv3 model...")
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

# Get YOLO output layer names
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Connect to ESP32-CAM
print("[INFO] Connecting to ESP32-CAM...")
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture("http://192.168.92.81:81/stream")
time.sleep(2.0)

# Last check timestamps
last_check_time = time.time()

# Flag to track break status
break_in_progress = False  # Face detection will pause if True

# PyQt6 Break Timer Class
class CountdownWindow(QWidget):
    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds
        self.initUI()
        self.start_countdown()

    def initUI(self):
        self.setWindowTitle("Break Timer")
        self.showFullScreen()  # Make the countdown full screenq

        self.layout = QVBoxLayout()

        self.label = QLabel(f"Time Remaining: {self.seconds} sec", self)
        self.label.setStyleSheet("font-size: 50px; font-weight: bold; color: orange;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    def start_countdown(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second

    def update_countdown(self):
        global break_in_progress

        if self.seconds > 0:
            self.seconds -= 1
            self.label.setText(f"Time Remaining: {self.seconds} sec")
        else:
            self.timer.stop()
            QMessageBox.information(self, "Break Over", "Time's up! Get back to work.")
            self.close()
            break_in_progress = False  # Resume face detection

    def closeEvent(self, event):
        if self.seconds > 0:
            event.ignore()  # Prevent closing before countdown ends

# Function to ask for a break
def ask_for_break():
    global break_in_progress

    app = QApplication(sys.argv)

    msg_box = QMessageBox()
    msg_box.setWindowTitle("Break Reminder")
    msg_box.setText("Do you want to take a break?")
    msg_box.setStyleSheet("font-size: 20px;")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

    result = msg_box.exec()

    if result == QMessageBox.StandardButton.Ok:
        break_in_progress = True  # Pause detection
        countdown = CountdownWindow(20)  # 20-second countdown
        countdown.show()
        sys.exit(app.exec())  # Keep the app running
    else:
        break_in_progress = False  # Resume detection
        sys.exit()  # Exit if the user cancels

# Function to insert detection status into MongoDB
def insert_detection_status(status):
    collection.insert_one({
        'status': status,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

# Function to check the last 5 statuses in MongoDB
def check_last_five_statuses():
    last_five = list(collection.find().sort("timestamp", -1).limit(6))
    if len(last_five) < 5:
        return False  # Not enough data yet
    return all(entry['status'] == "Face Detected" for entry in last_five)

# Function to clear all statuses in MongoDB after a break
def clear_last_five_statuses():
    collection.delete_many({})  # Clear all documents in the collection
    print("[INFO] Cleared all statuses from MongoDB.")

try:
    while True:
        if break_in_progress:
            print("[INFO] Break in progress... Face detection is paused.")
            time.sleep(1)
            continue  # Skip detection loop

        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame from ESP32-CAM")
            break

        # Resize frame for YOLO
        frame_resized = cv2.resize(frame, (416, 416))
        (h, w) = frame.shape[:2]

        # Convert frame to YOLO blob
        blob = cv2.dnn.blobFromImage(frame_resized, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        detections = net.forward(output_layers)

        person_detected = False
        highest_confidence = 0
        best_box = None

        for output in detections:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5 and class_id == 0:  # Class 0 = Person
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        box = detection[:4] * np.array([w, h, w, h])
                        best_box = box.astype("int")

        if best_box is not None:
            (centerX, centerY, width, height) = best_box
            startX = int(centerX - (width / 2))
            startY = int(centerY - (height / 2))
            endX = startX + width
            endY = startY + height

            # Draw bounding box
            color = (0, 255, 0)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            label = f"Person: {highest_confidence:.2f}"
            cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            person_detected = True

        # Show frame
        cv2.imshow("ESP32-CAM YOLOv3 Person Detection", frame)

        # Update MongoDB every 10 seconds
        if time.time() - last_check_time >= 10:
            last_check_time = time.time()
            status = "Face Detected" if person_detected else "No Face Detected"
            threading.Thread(target=insert_detection_status, args=(status,)).start()
            print(f"Status: {status} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check last 5 statuses and trigger break reminder if needed
        if check_last_five_statuses():
            threading.Thread(target=ask_for_break).start()
            clear_last_five_statuses()
            time.sleep(5)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    cap.release()
    cv2.destroyAllWindows()
