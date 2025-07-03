import RPi.GPIO as GPIO
import time

class Servo:
    def __init__(self, servo_pin):
        self.servo_pin = servo_pin

    def setup(self):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servo_pin, GPIO.OUT)
    
        # Create PWM objects
        self.pin_pwm = GPIO.PWM(self.servo_pin, 50)

        # Start PWM
        self.pin_pwm.start(0)

    def calibrate(self):
        # Calibrate the servo to 0 degrees
        self.setAngle(0)
        time.sleep(1)

    def setAngle(self, angle):
        duty_cycle = 2 + (angle / 18) # Convert angle to duty cycle
        GPIO.output(self.servo_pin, True)
        self.pin_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)

    def stop(self):
        GPIO.output(self.servo_pin, False)
        self.pin_pwm.ChangeDutyCycle(0)
