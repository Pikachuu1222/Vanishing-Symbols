# main.py
import cv2
import numpy as np
from pythonosc import udp_client
from serial import Serial
import time

# ——— CONFIG ———
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE    = 9600
OSC_IP       = "127.0.0.1"
OSC_PORT     = 8000
CONF_THRESH  = 0.5
IOU_THRESH   = 0.45

# load YOLOv4 face detector (compatible .cfg + .weights or .mm)
net = cv2.dnn.readNet("models/yolov4-face.weights", "models/yolov4-face.cfg")
layer_names = net.getUnconnectedOutLayersNames()

# set up OSC client
osc = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

# open Arduino serial
ser = Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

# camera
cap = cv2.VideoCapture(0)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
MAX_AREA = W * H
MIN_AREA = 1

while True:
    _, frame = cap.read()
    blob = cv2.dnn.blobFromImage(frame, 1/255, (416,416), [0,0,0], 1, crop=False)
    net.setInput(blob)
    outs = net.forward(layer_names)

    # parse detections
    class_ids, confidences, boxes = [], [], []
    for out in outs:
        for det in out:
            conf = float(det[4])
            if conf > CONF_THRESH:
                x, y, w, h = (det[0]*W, det[1]*H, det[2]*W, det[3]*H)
                boxes.append([int(x-w/2), int(y-h/2), int(w), int(h)])
                confidences.append(conf)
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESH, IOU_THRESH)

    # compute weighted avg distance from face area
    total_wd, total_w = 0.0, 0.0
    if len(idxs) > 0:
        for i in idxs.flatten():
            x,y,w,h = boxes[i]
            area = w*h
            distance = MAX_AREA / max(area, MIN_AREA)
            weight   = 1.0 / distance
            total_wd += distance * weight
            total_w  += weight
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 2)

    avg_face_dist = (total_wd/total_w) if total_w>0 else (MAX_AREA/MIN_AREA)
    cv2.putText(frame, f"D={avg_face_dist:.1f}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # read sensor distance
    line = ser.readline().decode().strip()
    try:
        sensor_dist = float(line)
    except:
        sensor_dist = None

    # choose which metric to send (you can blend them too)
    prox_value = sensor_dist if sensor_dist is not None else avg_face_dist

    # send over OSC
    osc.send_message("/proximity", prox_value)

    # show locally
    cv2.imshow("Vanishing Symbols", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
