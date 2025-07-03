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

    def filterData(self, l, threshold):

        yc = self.distance + l/2

        upper_threshold = yc * (1 + self.threshold)
        lower_threshold = yc * (1 - self.threshold)

        self.filteredData = self.data[(self.data.y >= lower_threshold) & (self.data.y <= upper_threshold)] 
        
        self.snr = 10 * np.log10(self.filteredData.snr)
        self.noise = 10 * np.log10(self.filteredData.noise)
        self.snr_linear = self.filteredData.snr

        print("FILTERED DATA:")
        print(self.filteredData)

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
        self.avgsnr = self.snr.groupby(self.filteredData.cycle).mean()
        self.avgsnr_linear = self.snr_linear.groupby(self.filteredData.cycle).mean()

    def dataMetrics(self):

        # 1. Ratio of filtered/gross points
        self.ratio = len(self.filteredData) / len(self.data)
        print(f"Test: {self.testname}")
        print(f"Filtered/Gross point ratio: {self.ratio}")

        if self.filteredData.empty or self.snr.empty:
            print("No filtered data available for metrics or plotting.")
            self.rcs = []
            self.error = []
            return
        
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
            if cycle in self.avgsnr_linear.index:
                currentRCS = (self.avgsnr_linear[cycle]*(4*np.pi)**3*(self.distance**4)*k*T*B*L)/(Pt*(G**2)*(lamb**2))
                self.rcs.append(currentRCS)
            else:
                self.rcs.append(np.nan)  # O el valor que prefieras para ciclos sin datos

        # 3. Error (distancemeter distance vs radar distance)
        self.error = []

        for i in range(len(self.cycles)):
            currentError = abs(self.centroids_y[i] - self.distance)
            self.error.append(currentError)

        # 4. Plot results

        fig, axs = plt.subplots(1, 3, figsize=(18, 5))

        # Average SNR per cycle
        axs[0].plot(self.cycles, self.avgsnr, color='green')
        axs[0].set_title('Average SNR per cycle')
        axs[0].set_xlabel('Cycle')
        axs[0].set_ylabel('SNR (dB)')
        axs[0].set_ylim(0, 30)
        axs[0].grid()

        # RCS per cycle
        axs[1].plot(self.cycles, self.rcs,color='blue')
        axs[1].set_title('RCS per cycle')
        axs[1].set_xlabel('Cycle')
        axs[1].set_ylabel('RCS (m²)')
        ylim = np.nanmean(self.rcs) + 1.2 * np.nanmean(self.rcs)
        axs[1].set_ylim(0, ylim)
        axs[1].grid()

         # Error per cycle
        axs[2].plot(self.cycles, self.error,color='orange')
        axs[2].set_title('Error per cycle')
        axs[2].set_xlabel('Cycle')
        axs[2].set_ylabel('Error (m)')
        axs[2].set_ylim(0, 0.5)
        axs[2].grid()

        fig.suptitle(f'Test: {self.testname}')

        plt.tight_layout(w_pad=3,rect=[0.05, 0, 1, 1])
        plt.show()

        '''# Average SNR per cycle
        plt.figure()
        plt.plot(self.cycles, self.avgsnr)
        plt.title(f'Average SNR | Test: {self.testname}')
        plt.xlabel('Cycle')
        plt.ylabel('SNR (dB)')
        plt.ylim(0,30)
        plt.grid()
        plt.show()

        # RCS per cycle
        plt.figure()
        plt.plot(self.cycles, self.rcs)
        plt.title(f'RCS | Test: {self.testname}')
        plt.xlabel('Cycle')
        plt.ylabel('RCS (m²)')
        ylim = np.mean(self.rcs) + 1.2*np.mean(self.rcs)
        plt.ylim(0,ylim)
        plt.grid()
        plt.show()

        # Error per cycle
        plt.figure()
        plt.plot(self.cycles, self.error)
        plt.title(f'Error | Test: {self.testname}')
        plt.xlabel('Cycle')
        plt.ylabel('Error (m)')
        plt.ylim(0,0.5)
        plt.grid()
        plt.show()'''

threshold = 0.25
    
test1 = Test('BASE_ONLY_0.5m.csv', 'BASE_ONLY_0.5m', 0.5, threshold)
test2 = Test('BASE_ONLY_1m.csv', 'BASE_ONLY_1m', 1.0, threshold)
test3 = Test('BASE_ONLY_1.5m.csv', 'BASE_ONLY_1.5m', 1.5, threshold)
test4 = Test('UNDER_RFL_0.5m.csv', 'UNDER_RFL_0.5m', 0.5, threshold)
test5 = Test('UNDER_RFL_1m.csv', 'UNDER_RFL_1m', 1.0, threshold)
test6 = Test('UNDER_RFL_1.5m.csv', 'UNDER_RFL_1.5m', 1.5, threshold)
test7 = Test('UNDER_RFL_2m.csv', 'UNDER_RFL_2m', 2.0, threshold)
test8 = Test('UNDER_RFL_2.5m.csv', 'UNDER_RFL_2.5m', 2.5, threshold)
test9 = Test('UNDER_RFL_3m.csv', 'UNDER_RFL_3m', 3.0, threshold)
test10 = Test('UNDER_RFL_4m.csv', 'UNDER_RFL_4m', 4.0, threshold)
test11 = Test('UNDER_RFL_5m.csv', 'UNDER_RFL_5m', 5.0, threshold)
test12 = Test('UNDER_RFL_7.5m.csv', 'UNDER_RFL_7.5m', 7.5, threshold)
test13 = Test('UNDER_RFL_8.9m.csv', 'UNDER_RFL_9m', 8.9, threshold)
test14 = Test('UNDER_RFL_9.5m.csv', 'UNDER_RFL_9.5m', 9.5, threshold)
test15 = Test('UNDER_RFL_10m.csv', 'UNDER_RFL_10m', 10.0, threshold)

tests = [test1, test2, test3, test4, test5, test6, test7, test8, test9, test10, test11, test12, test13, test14, test15]
distances = []
for test in tests:
    test.readData()
    test.filterData(0.2,0.25)
    test.calculateCentroids()
    test.averageSNR()
    test.dataMetrics()
    distances.append(test.distance)

distances = list(dict.fromkeys(distances))
print(distances)


# Plot ratio of filtered/gross points vs distance
distances_norfl = []
distances_rfl = []
ratios_norfl = []
ratios_rfl = []

tests_norfl = [test1, test2, test3]
tests_rfl = [test4, test6, test7, test9, test10, test11, test12, test13, test14, test15]

for test in tests_norfl:
    ratios_norfl.append(test.ratio)
    distances_norfl.append(test.distance)

for test in tests_rfl:
    ratios_rfl.append(test.ratio)
    distances_rfl.append(test.distance)


plt.figure()
plt.plot(distances_norfl, ratios_norfl)
plt.ylim(0,1)
plt.title('Filtering ratio vs distance, no reflectors')
plt.xlabel('Distance (m)')
plt.ylabel('Ratio of filtered/gross points')
plt.grid()
plt.show()

plt.figure()
plt.plot(distances_rfl, ratios_rfl)
plt.ylim(0,1)
plt.title('Filtering ratio vs distance, with reflector')
plt.xlabel('Distance (m)')
plt.ylabel('Ratio of filtered/gross points')
plt.grid()
plt.show()

# Plot error vs distance

error_norfl = []
error_rfl = []

for test in tests_norfl:
    error_norfl.append(np.mean(test.error))

for test in tests_rfl:
    error_rfl.append(np.mean(test.error))

mean_error_norfl = np.nanmean(error_norfl)
mean_error_rfl = np.nanmean(error_rfl)
#print(error_rfl)
#print(mean_error_rfl)

plt.figure()
plt.plot(distances_norfl, error_norfl)
plt.axhline(mean_error_norfl, color='red', linestyle='--', label='Mean error')
plt.title('Error vs distance, no reflectors')
plt.xlabel('Distance(m)')
plt.ylabel('Error (m)')
plt.ylim(0,0.5)
plt.legend()
plt.grid()
plt.show()

plt.figure()
plt.plot(distances_rfl, error_rfl)
plt.axhline(mean_error_rfl, color='red', linestyle='--', label='Mean error')
plt.title('Error vs distance, with reflector')
plt.xlabel('Distance(m)')
plt.ylabel('Error (m)')
plt.ylim(0,0.5)
plt.legend()
plt.grid()
plt.show()
