# LuminiView_Device_HCI_Project

The LuminiView, Eye Strain Reduction System helps reduce eye strain, musculoskeletal discomfort, and fatigue caused by prolonged screen time. It monitors the user's distance from the screen, reminds them to take regular breaks following the 20-20-20 rule, and tracks ambient lighting for a comfortable viewing experience. By using advanced sensors and real-time alerts, the system encourages healthier screen habits and enhances overall comfort during extended screen use.

## Installation

To set up the Drowning Detection project, follow these steps:

1. **Clone the Project:** :
```bash
   git clone https://github.com/KL193/LuminiView_Device_HCI_Project.git
```
2. **Create a Virtual Environment in Local Machine :**
```bash
  python -m venv env
```
3. **Install Requirements usin requirment.txt File :**
```bash
  For virtualenv to install all files included on the requirements.txt file.

      1.cd to the directory where requirements.txt is located
      2.activate your virtualenv
      3.run: pip install -r requirements.txt on your shell
```
4. **Upload mictrocontrollers code to esp32 board and esp32 camera model:**
  ```bash
  update wifi credentials with respect to available network

      // WiFi Credentials
            const char *ssid = "***********";
            const char *password = "********";
```
5. **After connect the esp32 camera get the overlay link:**
  ```bash
      cap = cv2.VideoCapture("http://192.168.92.81:81/stream")

  ```
  http://192.168.92.81:81 this type of link is appears in the serial monitor in arduino ide after upload the camfeed code to esp32 camera.

6.Requirements for API server

  a. Node.js and npm: Ensure Node.js (with npm) is installed on your system. You can check by 
     running:
  ```bash
              node -v
              npm -v      
  ```
  If not installed, download from https://nodejs.org.

  b. Express – For building the API server.
  ```bash
             npm install express   
  ```
  c. Mongoose – For connecting to MongoDB.
  ```bash
             npm install mongoose
  
  ```
  d. MongoDB Connection:Ensure your MongoDB connection string is correctly configured in 
    app.js.
   ```bash
  mongoose.connect('mongodb+srv://<username>:                    
            <password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority', {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        })

  ```
 Replace <username>, <password>, and <dbname> with your MongoDB credentials.  
 e. start the API Server:
  ```bash
             node app.js
  ```
  The server will be running at:
  ```bash
             http://localhost:3000/status
  ```
  
## How It Works  

The system uses advanced sensors and computer vision technology to:  
- Monitor the user's distance from the screen to minimize eye strain.  
- Remind users to take regular breaks using the 20-20-20 rule for healthier vision.  
- Track ambient lighting to ensure optimal viewing conditions.  

It is built using ESP32-CAM for face and gaze detection, an ESP32 board for processing, and various sensors for distance tracking and light intensity measurement.  

---

## Features  

- Real-time distance monitoring to reduce eye strain  
- Break reminders following the 20-20-20 rule  
- Ambient lighting tracking for optimal viewing conditions  
- Audible notifications to reinforce visual alerts  
- User-friendly OLED display for real-time data  


## Project Structure 
```
Eye-Strain-Reduction-System/  
│  
├── env/                     Virtual environment for dependencies  
│  
├── HCI_Project/              Main project directory  
│   ├── esp32camfeed/          ESP32-CAM image capture and feed  
│   └── esp32board/            ESP32 board logic and communication  
│  
├── hci_api/                  API for data processing and alerts  
│   └── app.js                Main server file for API endpoints  
│   └── package.json           Node.js dependencies  
│  
└── real-time/                Real-time object detection  
    ├── coco.names             Class labels for YOLO model  
    ├── yolov3.cfg             YOLOv3 configuration file  
    ├── yolov3.weights          YOLOv3 pre-trained weights  
    └── real_time.py           Script for real-time object detection  
    └── requirements.txt        Python dependencies  
    └── .gitignore              Git ignore file  
    └── real_time.gif           Demo of real-time detection  
│  
└── tk8616-src/               Source files for OLED screen integration  
└── azure.txt                 Azure configuration details  

```
## Demostration
[Here's](https://youtu.be/nZcInMJsQQk) a demonstration video of our luminiview eye strain reduction  system in action
