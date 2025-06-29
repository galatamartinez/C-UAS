import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

class Test:
    def __init__(self, filename, testname, axis, distance, threshold):
        self.filename = filename
        self.testname = testname
        self.axis = axis # Measurement configuration
        self.distance = distance
        self.threshold = threshold

    def readData(self):
        self.data = pd.read_csv(self.filename)
        self.cycle = self.data.cycle
        self.object = self.data.object
        self.x = self.data.x
        self.y = self.data.y
        self.z = self.data.z
        self.snr = 10 * np.log10(self.data.snr) # Convert to dB
    
    def filterData(self):

        # Define limits
        upper_threshold = self.distance * (1 + self.threshold)
        lower_threshold = self.distance * (1 - self.threshold)

        # Remove data outside the limits depending on the axis
        if self.axis == 'x':
            self.filteredData = self.data[(self.data.x >= lower_threshold) & (self.data.x <= upper_threshold)]
        elif self.axis == 'y':
            self.filteredData = self.data[(self.data.y >= lower_threshold) & (self.data.y <= upper_threshold)] 
        elif self.axis == 'z':
            self.filteredData = self.data[(self.data.z >= lower_threshold) & (self.data.z <= upper_threshold)]
        
    def averageData(self):

        self.snr = 10 * np.log10(self.filteredData.snr) # Convert to dB
        snr_avg = self.snr.groupby(self.cycle).mean()
        self.snr_plot = snr_avg.values
        self.cycle_plot = snr_avg.index.values

    def plotData(self):
        plt.plot(self.cycle_plot, self.snr_plot)

# Establish threshold percentage
threshold = 0.2

# Test 1: White wall
test1 = Test('test_white_wall.csv', 'White wall', 'y', 1.017, threshold)
test1.readData()
test1.filterData()
test1.averageData()

# Test 2: Blue paint
test2 = Test('test_blue_paint.csv', 'Blue paint', 'z', 0.78, threshold)
test2.readData()
test2.filterData()
test2.averageData()

# Test 3: White paint
test3 = Test('test_white_paint.csv', 'White paint', 'y', 0.732, threshold)
test3.readData()
test3.filterData()
test3.averageData()

# Test 4: Whiteboard
test4 = Test('test_whiteboard.csv', 'Whiteboard', 'y', 0.559, threshold)
test4.readData()
test4.filterData()
test4.averageData()

# Test 5: Gray heater (1)
test5 = Test('test_heater.csv', 'Gray heater (1)', 'x', 2.785, threshold)
test5.readData()
test5.filterData()
test5.averageData()

# Test 6: Gray heater (2)
test6 = Test('test_heater_2.csv', 'Gray heater (2)', 'y', 1.261, threshold)
test6.readData()
test6.filterData()
test6.averageData()

# Test 7: White plastic
test7 = Test('test_white_plastic.csv', 'White plastic', 'y', 0.922, threshold)
test7.readData()
test7.filterData()
test7.averageData()

# Test 8: Green PLA
test8 = Test('test_green_plastic.csv', 'Green PLA', 'y', 0.203, threshold)
test8.readData()
test8.filterData()
test8.averageData()

# Test 9: Black plastic
test9 = Test('test_black_plastic.csv', 'Black plastic', 'y', 0.406, threshold)
test9.readData()
test9.filterData()
test9.averageData()

# Rectangles to separate reflectivity values
low_rect = patches.Rectangle((1,0), 19, 10, facecolor = 'red', alpha = 0.2)
medium_rect = patches.Rectangle((1,10), 19, 10, facecolor = 'orange', alpha = 0.2)
high_rect = patches.Rectangle((1,20), 19, 10, facecolor = 'green', alpha = 0.2)

# Plot values
fig, ax = plt.subplots(figsize = (9, 6))

# Plot tests
test1.plotData()
test2.plotData()
test3.plotData()
test4.plotData()
test5.plotData()
test6.plotData()
test7.plotData()
test8.plotData()
test9.plotData()

# Add rectangles
ax.add_patch(low_rect)
ax.add_patch(medium_rect)
ax.add_patch(high_rect)
plt.xlabel('Cycle')
plt.ylabel('SNR (dB)')
plt.legend([test1.testname, test2.testname, test3.testname, test4.testname, test5.testname, test6.testname, test7.testname, test8.testname, test9.testname], loc = 'upper right')
plt.text(10, 5, 'Low reflectivity', ha='center', va='center', fontsize = 10, color = 'red')
plt.text(10, 15, 'Medium reflectivity', ha='center', va='center', fontsize = 10, color = 'orange')
plt.text(10, 25, 'High reflectivity', ha='center', va='center', fontsize = 10, color = 'green')
plt.xticks(test1.cycle_plot)
plt.tick_params(axis='x', which = 'both', labelsize = 10, pad = 12)
plt.show()