# sensor_to_touchdesigner.py
from serial import Serial
from pythonosc import udp_client
import time

# SERIAL_PORT = adjust if needed
ser = Serial("/dev/ttyACM0", 9600, timeout=1)
time.sleep(2)

client = udp_client.SimpleUDPClient("127.0.0.1", 8000)

while True:
    raw = ser.readline().decode().strip()
    try:
        d = float(raw)
        client.send_message("/proximity", d)
    except ValueError:
        pass
    time.sleep(0.05)
