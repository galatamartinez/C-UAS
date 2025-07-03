import smbus
import time
import numpy as np

class MPU6050:
    def __init__(self, address=0x68):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.bus.write_byte_data(self.address, 0x6B, 0)  # Wake up the MPU6050

        self.accel_sensitivity = 16384.0  # Sensitivity for accelerometer (2g range)
        self.gyro_sensitivity = 131.0      # Sensitivity for gyroscope (250 degrees/s range)
        self.last_time = time.time()

        # Initial angles for gyro
        self.pitch_gyro = 0.0
        self.roll_gyro = 0.0

        # Angles for complementary filter
        self.pitch = 0.0
        self.roll = 0.0

    def readWord(self, adress):
        high = self.bus.read_byte_data(self.address, adress)
        low = self.bus.read_byte_data(self.address, adress+1)
        value = (high << 8) + low

        if value >= 32768:
            return value - 65536   
        else:
            return value
    
    def readAngles(self):
        # Read accelerometer data
        Ax = self.readWord(0x3B)/self.accel_sensitivity
        Ay = self.readWord(0x3D)/self.accel_sensitivity
        Az = self.readWord(0x3F)/self.accel_sensitivity

        # Read gyroscope data
        Gx = self.readWord(0x43)/self.gyro_sensitivity
        Gy = self.readWord(0x45)/self.gyro_sensitivity
        Gz = self.readWord(0x47)/self.gyro_sensitivity

        return Ax, Ay, Az, Gx, Gy, Gz
    
    def computeAngles(self):
        Ax, Ay, Az, Gx, Gy, Gz = self.readAngles()

        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        # Calculate pitch and roll from accelerometer
        pitch_acc = np.arctan2(Ay, np.sqrt(Ax**2+Az**2)) * 180/np.pi
        roll_acc = np.arctan2(-Ax,Az) * 180/np.pi

        # Calculate pitch and roll from gyroscope
        self.pitch_gyro += Gy * dt
        self.roll_gyro += Gx * dt

        # Combine sensor data using complementary filter
        alpha = 0.98
        self.pitch = alpha * self.pitch_gyro + (1 - alpha) * pitch_acc
        self.roll = alpha * self.roll_gyro + (1 - alpha) * roll_acc

        return self.pitch, self.roll
    
    def printAngles(self):
        pitch, roll = self.computeAngles()
        print(f"Pitch: {pitch}º | Roll: {roll}º")


        


    