import RPi.GPIO as gpio
import time
from tuning import Tuning
import usb.core
import usb.util
import serial

gpio_pin_h = 18
gpio_pin_v = 12

gpio.setmode(gpio.BCM)
gpio.setup(gpio_pin_h, gpio.OUT)
gpio.setup(gpio_pin_v, gpio.OUT)

gs90_pwm_h = gpio.PWM(gpio_pin_h, 50)
gs90_pwm_v = gpio.PWM(gpio_pin_v, 50)

gs90_pwm_h.start(0)
gs90_pwm_v.start(0)

def gs90_angle(pwm, angle):
    if isinstance(angle, str):
        if angle.upper() == 'STOP':
            pwm.ChangeDutyCycle(0)
        else:
            print('wrong input')
    elif isinstance(angle, int) or isinstance(angle, float):
        pwm.ChangeDutyCycle(2.5 + angle * 10 / 180)

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

if dev:
    Mic_tuning = Tuning(dev)

def get_direction_angle():
    try:
        angle = Mic_tuning.direction
        return int(angle)
    except Exception as e:
        print("Error getting direction angle: {}".format(e))
        return None

def read_distance_once(port="/dev/ttyACM0", baudrate=921600):
    ser = serial.Serial(port, baudrate, timeout=1)
    data = ser.read(1024)
    hex_data = data.encode('hex')
    start = hex_data.find('542c')
    if start != -1:
        end = start + 94
        packet = hex_data[start:end]
        distances = []
        for i in range(6, 42, 3):
            byte1 = packet[i*2:i*2+2]
            byte2 = packet[i*2+2:i*2+4]
            distance_hex = byte2 + byte1
            distance = int(distance_hex, 16)
            distances.append(distance)
        average_distance = sum(distances) / len(distances)
        print("Average Distance:", average_distance)
        return average_distance
    return None

def control_servo(angle):
    try:
        gs90_angle(gs90_pwm_h, angle)
        distance = read_distance_once()
        if distance is not None:
            print("Distance read successfully:", distance)
    except Exception as e:
        print("Error controlling servo: {}".format(e))

def main():
    while True:
        angle = get_direction_angle()
        if angle is not None:
            print("Angle obtained: {}".format(angle))
            if 0 <= angle <= 180:
                control_servo(angle)
            else:
                print("Angle out of range for servo control.")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    finally:
        gs90_pwm_h.stop()
        gs90_pwm_v.stop()
        gpio.cleanup()
