from urad import *

# Input parameters for class Radar

enhancedPortName = 'COM5'
standardPortName = 'COM6'
testName = 'SURROUND_RFL_1.5m'
configFileName = 'chirp_default_copy.cfg'
pointCloudFileName = 'SURROUND_RFL_1.5m.csv'

# Configuration options for the program

saveData = True # Save data frame to .csv
plotData = True # Plot data
saveFrames = False # Save plot frames to .png

nOfCycles = 20 # Number of readings

radar = Radar(enhancedPortName, standardPortName, testName, configFileName, pointCloudFileName, nOfCycles)
radar.readConfigFile()
radar.configuratePorts()
radar.writeCommands()

for cycleCounter in range(1, nOfCycles+1):

    radar.standardPort.reset_input_buffer()
    radar.standardPort.reset_output_buffer()

    if radar.unpackData():
        radar.extractData(cycleCounter)
        if(plotData):
            radar.plotData(cycleCounter, saveFrames)
    
    #sleep(0.5)

if(saveData):
    radar.saveData()

radar.closePorts()

plt.ioff()
plt.show()

#print(f"Total objects: {len(radar.data.object)}")