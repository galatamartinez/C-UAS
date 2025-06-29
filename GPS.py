import serial
import numpy as np
import pandas as pd
import time

class GPS:
    def __init__(self, port):
        self.port = port
        
    def configuratePort(self):
        self.gps_port = serial.Serial(port=self.port, baudrate=9600, timeout=1)
        self.gps_port.reset_input_buffer()
        self.gps_port.reset_output_buffer()

    def readSentence(self):
        self.sentence = self.gps_port.readline().decode('ascii', errors='replace').strip()

    def parseGPGGA(self, sentence):
        parts = sentence.split(',')

        # 0. Identifier (in this case it must be GPGGA)
        if parts[0] != '$GPGGA' or len(parts) < 15:
            return None
        
        # 1. Time (UTC) format hhmmss
        time_utc = parts[1]

        # 2. Latitude, format DDMM.MMMM (D is degrees, M is minutes)
        latitude_degmin = parts[2]
        degrees = int(latitude_degmin[:2])
        minutes = float(latitude_degmin[2:])
        latitude = degrees + minutes/60

        # 3. Latitude direction (north or south)
        lat_direction = parts[3]
        if lat_direction == 'S':
            latitude *= -1 # Invert latitude value depending on direction

        # 4. Longitude, format DDMM.MMMM (D is degrees, M is minutes)
        longitude_degmin = parts[4]
        degrees = int(longitude_degmin[:2])
        minutes = float(longitude_degmin[2:])
        longitude = degrees + minutes/60

        # 5. Longitude direction (east or west)
        lon_direction = parts[5]
        if lon_direction == 'W':
            longitude *= -1 # Invert longitude value depending on direction

        # 6. Fix quality
        fix_quality = parts[6]

        # 7. Number of satellites
        satellites = parts[7]

        # 8. Horizontal dilution
        dilution = parts[8]

        # 9. Altitude (m)
        altitude = parts[9]

        return latitude, longitude, fix_quality, satellites, altitude
    
    def getPosition(self):
        latitude, longitude, fix_quality, satellites, altitude = self.parseGPGGA(self.sentence)

        # Save data into a dataframe
        self.gps_data = pd.DataFrame([{
            'latitude': latitude,
            'longitude': longitude,
            'fix_quality': fix_quality,
            'satellites': satellites,
            'altitude': altitude
        }])

        #print(gps_data)

    def closePort(self):
        self.gps_port.close()