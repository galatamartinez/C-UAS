import smbus
import numpy as np
from time import sleep

class HMC5883L:
    def __init__(self, address=0x1E):
        self.bus = smbus.SMBus(1)
        self.address = address

        # Initialize the sensor
        self.bus.write_byte_data(self.address, 0x00, 0x70) # Measurement and frequency config (default)
        self.bus.write_byte_data(self.address, 0x01, 0x20) # Gain (default)
        self.bus.write_byte_data(self.address, 0x02, 0x00) # Measurement mode (continuous)
        sleep(0.01)

    def readAxis(self, reg_high, reg_low):
        high = self.bus.read_byte_data(self.address, reg_high)
        low = self.bus.read_byte_data(self.address, reg_low)
        value = (high << 8) | low
        if value > 32767:
            value -= 65536
        return value

    def readData(self):
        Mx = self.readAxis(reg_high=0x03, reg_low=0x04)
        My = self.readAxis(reg_high=0x07, reg_low=0x08)
        Mz = self.readAxis(reg_high=0x05, reg_low=0x06)
        

        return Mx, My, Mz
    
    def computeYaw(self):
        Mx,My,Mz = self.readData()
        yaw_rad = np.arctan2(My,Mx) # Radians
        yaw_deg = np.rad2deg(yaw_rad) # Degrees
        yaw = yaw_deg % 360 # Ensure angle is within 0-360º

        return yaw
    
    def computeYawTiltCompensation(self, pitch, roll):
        # Correct yaw angle with MPU measurements
        Mx,My,Mz = self.readData()
        Mx_corrected = Mx*np.cos(pitch) + Mz*np.sin(pitch)
        My_corrected = Mx*np.sin(roll)*np.sin(pitch) + My*np.cos(roll) - Mz*np.sin(roll)*np.cos(pitch)

        yaw_rad = np.arctan2(My_corrected, Mx_corrected) # Radians
        yaw_deg = np.rad2deg(yaw_rad) # Degrees
        self.yaw = yaw_deg % 360 # Ensure angle is within 0-360º
    
    def printYaw(self):
        #yaw = self.computeYaw()
        #yaw = self.computeYawTiltCompensation()
        print(f"Heading: {self.yaw}º")