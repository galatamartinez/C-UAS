import RPi.GPIO as GPIO
import time

# Define servo pins
pitch_pin = 12
yaw_pin = 13

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(pitch_pin, GPIO.OUT)
GPIO.setup(yaw_pin, GPIO.OUT)

# Create PWM instances
pitch_pwm = GPIO.PWM(pitch_pin, 50)  # 50 Hz
yaw_pwm = GPIO.PWM(yaw_pin, 50)    # 50 Hz

# Start PWM
pitch_pwm.start(0)
yaw_pwm.start(0)

# Function to set angle
def set_angle(angle):
    duty_cycle = 2 + (angle/18)  # Convert angle to duty cycle
    GPIO.output(pitch_pin, True)
    pitch_pwm.ChangeDutyCycle(duty_cycle)
    GPIO.output(yaw_pin, True)
    yaw_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    GPIO.output(pitch_pin, False)
    GPIO.output(yaw_pin, False)
    pitch_pwm.ChangeDutyCycle(0)
    yaw_pwm.ChangeDutyCycle(0)

while True:
    for angle in [0,90,180]:
        print(f"Setting pitch and yaw to {angle} degrees")
        set_angle(angle)
        time.sleep(1)