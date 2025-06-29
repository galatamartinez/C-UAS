import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd

class Test:
    def __init__(self, filename, testname, distance, threshold):
        self.filename = filename
        self.testname = testname
        self.distance = distance
        self.threshold = threshold

    def readData(self):
        self.data = pd.read_csv(self.filename)
        self.cycle = self.data.cycle
        self.object = self.data.object
        self.x = self.data.x
        self.y = self.data.y
        self.z = self.data.z
        self.cycles = sorted(self.data.cycle.unique())

    def filterData(self, l, w, h, threshold):

        # Given drone principal dimensions (length, width, height), filter data within a defined sphere
        # Center position will be stablished around the measured distance

        xc = 0
        yc = self.distance + l/2
        zc = 0

        # Define sphere radius (higher dimension of the drone + margin)
        self.r = max(l, w, h)*(1 + threshold)

        # Calculate distance to the center and filter data
        dist = np.sqrt((self.x - xc)**2 + (self.y -yc)**2 + (self.z - zc)**2)
        inside_sphere = dist <= self.r

        self.filteredData = self.data[inside_sphere]
        self.snr = 10 * np.log10(self.filteredData.snr)
        self.noise = 10 * np.log10(self.filteredData.noise)
        self.snr_linear = self.filteredData.snr

    def calculateCentroids(self):

        # Calculate centroids of each point cloud (per cycle)
        self.centroids_x = []
        self.centroids_y = []
        self.centroids_z = []

        for cycle in self.cycles:
            currentCycleData = self.filteredData.loc[self.filteredData['cycle'] == cycle]

            currentX = currentCycleData.x
            currentY = currentCycleData.y
            currentZ = currentCycleData.z

            self.centroids_x.append(np.average(currentX))
            self.centroids_y.append(np.average(currentY))
            self.centroids_z.append(np.average(currentZ))

    def averageSNR(self):
        # Calculate average SNR for each cycle
        self.avgsnr = self.snr.groupby(self.cycle).mean()
        self.avgsnr_linear = self.snr_linear.groupby(self.cycle).mean()

    def SNRModelNoRLF(self):
        # Model SNR as an exponential function
        # SNR proportional to 1/distance^4
        # Reference value given by the closest distance test
        a =1
        
     

    def SNRModelRLF(self):
        # Model SNR as an exponential function
        # SNR proportional to 1/distance^4
        # Reference value given by the highest SNR test (medium to close distance)
        a = 1
        



    def dataMetrics(self):

        # 1. Ratio of filtered/gross points
        self.ratio = len(self.filteredData) / len(self.data)
        print(f"Test: {self.testname}")
        print(f"Filtered/Gross point ratio: {self.ratio}")
    
        # 2. RCS (Radar Cross Section)
        k = 1.38e-23 # Boltzmann constant (J/K)
        T = 290 # Temperature (K)
        B = 4e9 # Bandwidth (Hz)
        G = 1 # Antenna gain (linear)
        L = 1 # Loss factor (linear)
        Pt = 0.0316 # Transmitted power (W)
        f = 62e9 # Frequency (Hz)
        c = 3e8 # Speed of light (m/s)
        lamb = c / f # Wavelength (m)

        self.rcs = []

        for cycle in self.cycles:
            currentRCS = (self.avgsnr_linear[cycle]*(4*np.pi)**3*(self.distance**4)*k*T*B*L)/(Pt*(G**2)*(lamb**2))
            self.rcs.append(currentRCS)

        # 3. Error (distancemeter distance vs radar distance)
        self.error = []

        for i in range(len(self.cycles)):
            currentError = abs(self.centroids_y[i] - self.distance)
            self.error.append(currentError)

        # 4. Plot results

        # Average SNR per cycle
        plt.figure()
        plt.plot(self.cycles, self.avgsnr)
        plt.title(f'Average SNR | Test: {self.testname}')
        plt.xlabel('Cycle')
        plt.ylabel('SNR (dB)')
        plt.grid()
        plt.show()

        # RCS per cycle
        plt.figure()
        plt.plot(self.cycles, self.rcs)
        plt.title(f'RCS | Test: {self.testname}')
        plt.xlabel('Cycle')
        plt.ylabel('RCS (m²)')
        plt.grid()
        plt.show()

        # Error per cycle
        plt.figure()
        plt.plot(self.cycles, self.error)
        plt.title(f'Error | Test: {self.testname}')
        plt.xlabel('Cycle')
        plt.ylabel('Error (m)')
        plt.grid()
        plt.show()

    
test1 = Test('BASE_ONLY_0.5m.csv', 'BASE_ONLY_0.5m', 0.5, 0.25)
test2 = Test('BASE_ONLY_1m.csv', 'BASE_ONLY_1m', 1.0, 0.25)
test3 = Test('BASE_ONLY_1.5m.csv', 'BASE_ONLY_1.5m', 1.5, 0.25)
test4 = Test('BASE_ONLY_2m.csv', 'BASE_ONLY_2m', 2.0, 0.25)
test5 = Test('BASE_ONLY_2.5m.csv', 'BASE_ONLY_2.5m', 2.5, 0.25)
test6 = Test('BASE_ONLY_3m.csv', 'BASE_ONLY_3m', 3.0, 0.25)

tests = [test1, test2, test3, test4, test5, test6]
for test in tests:
    test.readData()
    test.filterData(0.5, 0.5, 0.5, 0.25)
    test.calculateCentroids()
    test.averageSNR()
    test.dataMetrics()