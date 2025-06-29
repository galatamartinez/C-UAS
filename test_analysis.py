import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import plotly.express as px
from test_class import *

# Establish threshold percentage
threshold = 0.2

# Tests with NO aluminum foil

test1 = Test('test_floor_1.csv', '0.654 m, no aluminum', 'y', 0.654, threshold)
test2 = Test('test_floor_2.csv', '0.326 m, no aluminum', 'y', 0.326, threshold)
test3 = Test('test_floor_3.csv', '0.270 m, no aluminum', 'y', 0.270, threshold)
test4 = Test('test_floor_4.csv', '0.173 m, no aluminum', 'y', 0.173, threshold)
test5 = Test('test_floor_5.csv', '0.872 m, no aluminum', 'y', 0.872, threshold)
test6 = Test('test_floor_6.csv', '1.12 m, no aluminum', 'y', 1.12, threshold)
test7 = Test('test_floor_7.csv', '1.304 m, no aluminum', 'y', 1.304, threshold)
test8 = Test('test_floor_8.csv', '1.641 m, no aluminum', 'y', 1.641, threshold)
test9 = Test('test_floor_9.csv', '1.844 m, no aluminum', 'y', 1.844, threshold)
test10 = Test('test_floor_10.csv', '2 m, no aluminum', 'y', 2, threshold)

# Tests with aluminum foil

test11 = Test('test_floor_1_al.csv', '0.193 m, aluminum', 'y', 0.193, threshold)
test12 = Test('test_floor_2_al.csv', '0.341 m, aluminum', 'y', 0.341, threshold)
test13 = Test('test_floor_3_al.csv', '0.476 m, aluminum', 'y', 0.476, threshold)
test14 = Test('test_floor_4_al.csv', '0.644 m, aluminum', 'y', 0.644, threshold)
test15 = Test('test_floor_5_al.csv', '0.801 m, aluminum', 'y', 0.801, threshold)
test16 = Test('test_floor_6_al.csv', '0.995 m, aluminum', 'y', 0.995, threshold)
test17 = Test('test_floor_7_al.csv', '1.229 m, aluminum', 'y', 1.229, threshold)
test18 = Test('test_floor_8_al.csv', '1.494 m, aluminum', 'y', 1.494, threshold)
test19 = Test('test_floor_9_al.csv', '1.782 m, aluminum', 'y', 1.782, threshold)
test20 = Test('test_floor_10_al.csv', '2.014 m, aluminum', 'y', 2.014, threshold)

tests = [test1, test2, test3, test4, test5, test6, test7, test8, test9, test10, test11, test12, test13, test14, test15, test16, test17, test18, test19, test20]

# Rectangles to separate reflectivity values
low_rect = patches.Rectangle((1,0), 19, 10, facecolor = 'red', alpha = 0.2)
medium_rect = patches.Rectangle((1,10), 19, 10, facecolor = 'orange', alpha = 0.2)
high_rect = patches.Rectangle((1,20), 19, 10, facecolor = 'green', alpha = 0.2)

distances = []
ratios = []
colors = []
legends = []

for test in tests:
    test.readData()
    test.filterData()
    test.averageData()
    test.dataMetrics()
    test.selectPointClouds()
    test.rotateData()
    test.plotPointCloud()
    distances.append(test.distance)
    ratios.append(test.ratio)
    legends.append(test.testname)
    test.averageData()
    test.plotData()
 
for i in range(len(tests)):
    if i < 10:
        colors.append('blue')
    else:
        colors.append('red')

# Analyze how the ratio of filtered/gross points changes with distance
plt.figure()
plt.scatter(distances, ratios, c=colors)
plt.xlabel('Distance (m)')
plt.ylabel('Ratio of Filtered/Gross Points')
plt.title('Distance vs Ratio of Filtered/Gross Points')
plt.grid(True)
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='No Aluminum'),
           plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Aluminum')]
plt.legend(handles=handles, loc='upper left')
plt.show()

# SNR analysis
fig1, ax1 = plt.subplots(figsize = (9, 6))

# Add rectangles
ax1.add_patch(low_rect)
ax1.add_patch(medium_rect)
ax1.add_patch(high_rect)

for test in tests:
    ax1.plot(test.cycle_plot, test.snr_plot, label=test.testname)

plt.xlabel('Cycle')
plt.ylabel('SNR (dB)')
plt.legend(legends, loc = 'lower right')
plt.text(10, 5, 'Low reflectivity', ha='center', va='center', fontsize = 10, color = 'red')
plt.text(10, 15, 'Medium reflectivity', ha='center', va='center', fontsize = 10, color = 'orange')
plt.text(10, 25, 'High reflectivity', ha='center', va='center', fontsize = 10, color = 'green')
plt.xticks(test1.cycle_plot)
plt.tick_params(axis='x', which = 'both', labelsize = 10, pad = 12)
plt.show()

# Compare unfiltered data aluminum vs no aluminum

# Define test pairs
compare_tests = [(test1, test14), (test2, test13), (test3, test12), (test4, test11), (test5, test15), (test6, test16), (test7, test17), (test8, test18), (test9, test19), (test10, test20)]

for i in range(len(compare_tests)):

    x1 = compare_tests[i][0].x_compare
    y1 = compare_tests[i][0].y_compare
    z1 = compare_tests[i][0].z_compare

    x2 = compare_tests[i][1].x_compare
    y2 = compare_tests[i][1].y_compare
    z2 = compare_tests[i][1].z_compare

    fig = plt.figure(figsize = (18, 6))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')

    ax1.scatter(x1,y1,z1)
    ax1.set_title(f'{compare_tests[i][0].testname}')
    ax1.set_xlim(-0.5,0.5)
    ax1.set_ylim(-0.5,0.5)
    ax1.set_zlim(-2,2)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')

    ax2.scatter(x2,y2,z2)
    ax2.set_title(f'{compare_tests[i][1].testname}')
    ax2.set_xlim(-0.5,0.5)
    ax2.set_ylim(-0.5,0.5)
    ax2.set_zlim(-2,2)
    ax2.set_xlabel('X')    
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')

    plt.show()
