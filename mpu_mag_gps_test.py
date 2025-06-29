import smbus
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx

from MPU6050 import *
from HMC5883L import *
from GPS import *

# Define sensors
mpu = MPU6050(address=0x68)
gps = GPS('/dev/tty/USB0') # CHECK FIRST!!! dmesg | grep tty
mag = HMC5883L(address=0x1E)

# Configurate sensors
gps.configuratePort()

# Start reading
mpu.readAngles()
gps.readSentence()
mag.readData()

while True:
    # Compute values
    mpu.computeAngles()
    gps.getPosition()
    mag.computeYawTiltCompensation(mpu.pitch, mpu.roll)

    # Display data
    print(f'Pitch: {mpu.pitch} | Roll: {mpu.roll} | Yaw: {mag.yaw}')
    print('--------GPS DATA--------')
    print(gps.gps_data)
    sleep(1)

