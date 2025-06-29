import serial
import struct
import numpy as np
import pandas as pd
from time import sleep
import matplotlib.pyplot as plt

class Radar:

    def __init__(self, enhancedPortName, standardPortName, testName, configFileName, pointCloudFileName, nOfCycles):

        # Ports and files names
        self.enhancedPortName = enhancedPortName
        self.standardPortName = standardPortName
        self.configFileName = configFileName
        self.pointCloudFileName = pointCloudFileName
        self.testName = testName

        # Syncronization pattern
        self.syncPattern = 0x708050603040102

        # Parameters for managing data packets and bytes received from the standard port
        self.packetHeader = bytearray([])
        self.headerLength = 40 # Header = 40 bytes
        self.tlvHeaderLength = 8 # TLV Header = 8 bytes

        # Arrays to save data
        self.cycles = []
        self.objects = []
        self.xArray = []
        self.yArray = []
        self.zArray = []
        self.vArray = []
        self.snrArray = []
        self.noiseArray = []

        # Number of measuring cycles
        self.nOfCycles = nOfCycles

        # Initialize the plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.ion()
        plt.show()

        # Initialize data DataFrame
        self.data = pd.DataFrame(columns=["cycle", "object", "x", "y", "z", "v", "snr", "noise"])

    def readConfigFile(self): # Open and read .cfg file

        self.counter = 0
        self.commands = []

        with open(self.configFileName, 'r') as fp:
            for line in fp:
                if (len(line) > 1):
                    if (line[0] != '%'):
                        self.commands.append(line)
                        self.counter += 1
            fp.close()

    def configuratePorts(self): # Define serial ports (enhanced = config, standard = data)

        self.enhancedPort = serial.Serial(port = self.enhancedPortName, baudrate = 115200, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 0.3)
        self.standardPort = serial.Serial(port = self.standardPortName, baudrate = 921600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 0.3)

        #self.standardPort.set_buffer_size(rx_size=16384,tx_size=16384)

        # Reset both input and output buffers to avoid old data issues
        self.standardPort.reset_input_buffer()
        self.standardPort.reset_output_buffer()

    def writeCommands(self): # Write the .cfg file commands to the enhanced port

        # Read initial response
        initialResponse = bytearray([])
        while(self.enhancedPort.in_waiting > 0): # Number of bytes in the input buffer > 0
            initialResponse += self.enhancedPort.read(1) 
        print(initialResponse.decode())

        # Write commands to the enhanced port
        for i in range(self.counter):
            self.enhancedPort.write(bytearray(self.commands[i].encode()))
            sleep(0.02)
            response = bytearray([])
            while(self.enhancedPort.in_waiting > 0): 
                response += self.enhancedPort.read(1) 
            print(response.decode())

    def unpackData(self):

        self.packetHeader += self.standardPort.read(self.headerLength - len(self.packetHeader))

        # Checking if the data packet has the desired size
        if len(self.packetHeader) != self.headerLength:    
            print("Incorrect buffer length, waiting for full header...")
            return False  # Wait until we have a full header

        # -------------------------------------------------------------------------
        # HEADER --> 40 BYTES
        # -------------------------------------------------------------------------

        # 1. Syncronization word (8 bytes) - Must match syncronization pattern (defined above)
        # This word indicates where the data packet begins. It works as an identifier

        # 2. SDK Version (4 bytes)

        # 3. Packet length (4 bytes)

        # 4. Platform (4 bytes)

        # 5. Frame number (4 bytes)

        # 6. Time (4 bytes)

        # 7. Number of detected objects (4 bytes)

        # 8. Number of TLVs (4 bytes)

        # 9. Sub-frame number (4 bytes)

        self.sync, self.version, self.packetLength, self.platform, self.frameNumber, self.timeCpuCycles, self.numOfDetectedObj, self.numOfTlvs, self.subFrameNumber = struct.unpack('Q8I', self.packetHeader[:self.headerLength])
        
        return True # Condition for unpacking data only when the header has the correct size
    
        # -------------------------------------------------------------------------
        # END OF THE HEADER
        # -------------------------------------------------------------------------
    
    def extractData(self, cycleCounter): 

        if (self.sync == self.syncPattern): # If we find where the data packet begins

            #print("Syncronization pattern match, extracting data...")

            self.packetHeader = bytearray([])

            # Packet payload: What we want to extract (position, speed and noise)
            # Total data packet consists of header + packet payload (TLV header is inside of the payload)
            self.packetPayload = self.standardPort.read(self.packetLength - self.headerLength)

            # Matrix for saving the packet payload data per detected object
            self.objectData = np.zeros((self.numOfDetectedObj, 6))
            #print(f"Detected objects: {self.numOfDetectedObj}")

            self.objectCounter = 1 # Reset object counter for the data frame

            for i in range(self.numOfTlvs):

                # -------------------------------------------------------------------------
                # TLV HEADER --> 8 BYTES
                # -------------------------------------------------------------------------

                # 1. TLV type (4 bytes)
                #    - Type 1: Gives position (x,y,z) and speed (v)
                #    - Type 7: Gives SNR and noise

                # 2. TLV length (4 bytes)
                
                self.tlvType, self.tlvLength = struct.unpack('2I', self.packetPayload[:self.tlvHeaderLength])

                if (self.tlvType > 20 or self.tlvLength > 10000):
                        self.packetHeader = bytearray([])
                        break
                
                # -------------------------------------------------------------------------
                # END OF THE TLV HEADER
                # -------------------------------------------------------------------------
                
                # Once we have the TLV header information, we extract it from the payload
                self.packetPayload = self.packetPayload[self.tlvHeaderLength:]

                if (self.tlvType == 1):

                    for k in range(self.numOfDetectedObj):

                        # Extracting position and speed, each element consists of 4 bytes

                        self.x, self.y, self.z, self.v = struct.unpack('4f', self.packetPayload[:16])

                        # Adding data to matrix
                        self.objectData[k,0] = self.x
                        self.objectData[k,1] = self.y
                        self.objectData[k,2] = self.z
                        self.objectData[k,3] = self.v

                        # Supressing the already read data from the packet payload
                        self.packetPayload = self.packetPayload[16:]

                        self.objects.append(self.objectCounter)
                        self.xArray.append(self.x)
                        self.yArray.append(self.y)
                        self.zArray.append(self.z)
                        self.vArray.append(self.v)
                        self.cycles.append(cycleCounter)
                        
                        self.objectCounter += 1

                elif (self.tlvType == 7): 

                    for n in range(self.numOfDetectedObj):

                        # Extracting SNR and noise, each element consists of 2 bytes

                        self.snr, self.noise = struct.unpack('2H', self.packetPayload[:4])

                        # Adding data to matrix
                        self.objectData[n,4] = self.snr
                        self.objectData[n,5] = self.noise

                        # Supressing the already read data from the packet payload
                        self.packetPayload = self.packetPayload[4:]

                        # Print all the extracted data
                        #print(f"x: {self.objectData[n,0]} m | y: {self.objectData[n,1]} m | z: {self.objectData[n,2]} m | v: {self.objectData[n,3]} m/s | SNR: {self.objectData[n,4]} dB | Noise: {self.objectData[n,5]} dB")

                        self.snrArray.append(self.snr)
                        self.noiseArray.append(self.noise)

            # Verify lists length
            min_length = min(len(self.cycles), len(self.objects), len(self.xArray), len(self.yArray), len(self.zArray), len(self.vArray), len(self.snrArray), len(self.noiseArray))

            # Data frame for the current cycle
            currentCycleData = pd.DataFrame(
            {
            "cycle": self.cycles[:min_length],
            "object": self.objects[:min_length],
            "x": self.xArray[:min_length],
            "y": self.yArray[:min_length],
            "z": self.zArray[:min_length],
            "v": self.vArray[:min_length],
            "snr": self.snrArray[:min_length],
            "noise": self.noiseArray[:min_length]
            })

            # Append data to the main data frame
            self.data = pd.concat([self.data, currentCycleData], ignore_index = True)

            # Reset the arrays for the next cycle
            self.cycles.clear()
            self.objects.clear()
            self.xArray.clear()
            self.yArray.clear()
            self.zArray.clear()
            self.vArray.clear()
            self.snrArray.clear()
            self.noiseArray.clear()

        else:
            # If syncronization pattern is not matching, we go forward one position in the header until it matches
            print("Syncronization pattern match not found, trying again...")
            self.packetHeader = self.packetHeader[1:]

    def saveData(self):
        print(self.data)
        self.data.to_csv(self.pointCloudFileName, index=False)

    def plotData(self, cycleCounter, saveFrames):

        cycleTable = self.data[self.data['cycle'] == cycleCounter]
        xCycle = cycleTable.x
        yCycle = cycleTable.y
        zCycle = cycleTable.z

        self.ax.cla()  # Clear graph
        self.ax.set_title(f"Cycle {cycleCounter}")
        self.ax.set(xlabel='X [m]')
        self.ax.set(ylabel='Y [m]')
        self.ax.set(zlabel='Z [m]')

        self.ax.set_xlim([-5, 5])
        self.ax.set_ylim([5, -5])
        self.ax.set_zlim([-5, 5])

        # Add information of the detected objects in the current cycle
        self.ax.text(x=-8,y=8,z=13.75,s=f"Detected objects: {self.numOfDetectedObj}")
        self.ax.scatter(xCycle, yCycle, zCycle)
        
        if(saveFrames):
            # Save frames to .png
            plt.savefig(fname=f"cycle_{cycleCounter}_test_{self.testName}.png")

        plt.draw()  # Update figure in each cycle
        plt.pause(0.25)

    def closePorts(self): # Closing ports at the end of each measuring

        if self.enhancedPort.is_open:
            self.enhancedPort.close()

        if self.standardPort.is_open:
            self.standardPort.close()
