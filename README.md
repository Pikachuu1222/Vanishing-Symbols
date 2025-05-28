# Vanishing-Symbols
Vanishing Symbols is an interactive public‐art installation that probes hidden symbolic violence in short‐video culture. Using proximity sensing and computer vision, it creates two states of visual patterns:
- Solidify: when people ignore the panels, bold, concrete shapes remain on–screen, symbolizing the unnoticed oppression in brief social videos.
- Disperse: as viewers approach and become aware, those shapes dissolve into particles and fade, inviting reflection on inequality’s subtle forces.

Under the hood it combines an Arduino‐based distance sensor, YOLOv4 face‐detector on a small “smart” camera, and TouchDesigner driven visuals—triggered via OSC messages—to close the loop between body, mind, and image.

![Solidify → Disperse](./assets/preview.gif)



## Features

- **Arduino distance sensing** (e.g. HC‐SR04, VL53L0X) to detect viewer proximity
- **Real‐time face detection** with YOLOv4 on an embedded camera
- **Weighted average “distance”** from multiple detections to drive visual dispersion
- **OSC messaging** from Python to TouchDesigner for dynamic visuals
- Two visual states:
  - **Solidify**: patterns remain bold when ignored
  - **Disperse**: patterns shatter into particles as viewers approach



## Hardware Setup

1. **Sensor**  
   - HC‐SR04 ultrasonic or VL53L0X Time-of-Flight module  
   - Connect VCC → 5 V, GND → GND, TRIG → D9, ECHO → D10 (HC‐SR04)  
2. **Smart Camera**  
   - Embedded Linux board (e.g. Jetson Nano or Raspberry Pi)  
   - USB camera or CSI camera  
3. **PC**  
   - Runs Python + OpenCV + YOLO  
   - Sends OSC to TouchDesigner (localhost:8000 by default)  
4. **TouchDesigner**  
   - Receives `/proximity` OSC messages  
   - Maps a custom particle system to the incoming value



## Software Requirements

- **Arduino IDE** (for uploading `ultrasonic_sensor.ino`)
- **Python 3.8+** with:
  - `opencv-python`
  - `numpy`
  - `pyserial`
  - `python-osc`
  - (if using Ultralytics) `ultralytics`
- **TouchDesigner 2021.20060+**



## Installation

```bash
# 1. Clone repo
git clone https://github.com/yourname/vanishing-symbols.git
cd vanishing-symbols

# 2. Create Python venv & install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Upload Arduino code
#    - Open arduino/ultrasonic_sensor.ino in Arduino IDE
#    - Select your board & port, then upload

# 4. Prepare YOLO model
#    - Download `yolov4-face.mm` or your face‐detector into models/

# 5. Launch
#    - Run Python face‐detector + OSC bridge:
python sensor_to_touchdesigner.py

#    - In another shell, run face‐detection:
python main.py

# 6. Open TouchDesigner project `TD/vanishing_symbols.toe`
#    - It listens for OSC on port 8000
