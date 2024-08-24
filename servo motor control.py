import RPi.GPIO as gpio
import time

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

if __name__ == '__main__':
    gs90_angle(gs90_pwm_h, 0)
    gs90_angle(gs90_pwm_v, 0)
    time.sleep(1)
    gs90_angle(gs90_pwm_h, 'stop')
    gs90_angle(gs90_pwm_v, 'stop')
    time.sleep(3)

    gs90_pwm_h.stop()
    gs90_pwm_v.stop()
    gpio.cleanup()
