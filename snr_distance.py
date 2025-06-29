import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from test_class import *

# Estimate SNR variation with distance with indoors tests

threshold = 0.25

# Model 1: BASE ONLY (no reflectors)

test1 = Test('BASE_ONLY_0.5m.csv', '0.5 m', 'y', 0.5, threshold)
test2 = Test('BASE_ONLY_1m.csv', '1.0 m', 'y', 1.0, threshold)
test3 = Test('BASE_ONLY_1.5m.csv', '1.5 m', 'y', 1.5, threshold)
test4 = Test('BASE_ONLY_2m.csv', '2.0 m', 'y', 2.0, threshold)
test5 = Test('BASE_ONLY_2.5m.csv', '2.5 m', 'y', 2.5, threshold)
test6 = Test('BASE_ONLY_3m.csv', '3.0 m', 'y', 3.0, threshold)

tests1 = [test1, test2, test3, test4, test5, test6]

distances1 = []
snr1 = []

for test in tests1:
    test.readData()
    test.filterData()
    test.averageData()
    distances1.append(test.distance)
    snr_linear = 10 ** (test.snr_plot / 10)  # Convert dB to linear scale
    snr1.append(snr_linear.mean())

# Fit curve to the data
snr1_fit = []
base_distance1 = distances1[0]
base_snr = snr1[0]
for i in range(len(snr1)):
    if i == 0:
        snr1_fit.append(base_snr)
    else:
        snr1_fit.append(snr1[i]*(base_distance1/distances1[i])**4)

snr1_db = 10 * np.log10(snr1)  # Convert back to dB for plotting
snr1_fit_db = 10 * np.log10(snr1_fit)  # Convert back to dB for plotting

# Plot original data vs fitted data
plt.figure()
plt.plot(distances1, snr1_db, color='blue', label='Measured SNR')
plt.plot(distances1, snr1_fit_db, color='green', label='Fitted SNR')
plt.axhline(0,color='red', linestyle='--', label='Detection threshold')
plt.xlabel('Distance (m)')
plt.ylabel('SNR (dB)')
plt.title('SNR vs Distance')
plt.grid(True)
plt.legend(loc='lower left')
plt.show()

# Calculate RCS vs distance
k = 1.38e-23 # Boltzmann constant (J/K)
T = 290 # Temperature (K)
B = 4e9 # Bandwidth (Hz)
G = 1 # Antenna gain (linear)
L = 1 # Loss factor (linear)
Pt = 0.0316 # Transmitted power (W)
f = 62e9 # Frequency (Hz)
c = 3e8 # Speed of light (m/s)
lamb = c / f # Wavelength (m)

rcs1 = []

for i in range(len(distances1)):
    currentRCS1 = (snr1_fit[i]*(4*np.pi)**3*(distances1[i]**4)*k*T*B*L)/(Pt*(G**2)*(lamb**2))
    rcs1.append(currentRCS1)

# Plot RCS vs distance 
plt.figure()
plt.plot(distances1, rcs1, color = 'blue')
plt.axhline(0.04, color='red', linestyle='--', label='Mini UAV typical RCS')
plt.axhline(0.5, color='red', linestyle='--')
plt.xlabel('Distance (m)')
plt.ylabel('RCS (m²)')
plt.ylim(0,1)
plt.grid(True)
plt.legend(loc='upper right')
plt.title('RCS vs Distance')
plt.show()

# Model 2: UNDER RFL (one reflector under the UAV)

test7 = Test('UNDER_RFL_0.5m.csv', '0.5 m', 'y', 0.5, threshold)
test8 = Test('UNDER_RFL_1m.csv', '1.0 m', 'y', 1.0, threshold)
test9 = Test('UNDER_RFL_1.5m.csv', '1.5 m', 'y', 1.5, threshold)
test10 = Test('UNDER_RFL_2m.csv', '2.0 m', 'y', 2.0, threshold)
test11 = Test('UNDER_RFL_2.5m.csv', '2.5 m', 'y', 2.5, threshold)
test12 = Test('UNDER_RFL_3m.csv', '3.0 m', 'y', 3.0, threshold)
test13 = Test('UNDER_RFL_4m.csv', '4 m', 'y', 4.0, threshold)
test14 = Test('UNDER_RFL_5m.csv', '5 m', 'y', 5.0, threshold)
test15 = Test('UNDER_RFL_7.5m.csv', '7.5 m', 'y', 7.5, threshold)
test16 = Test('UNDER_RFL_8.9m.csv', '8.9 m', 'y', 8.9, threshold)
test17 = Test('UNDER_RFL_9.5m.csv', '9.5 m', 'y', 9.5, threshold)
test18 = Test('UNDER_RFL_10m.csv', '10 m', 'y', 10.0, threshold)

tests2 = [test7, test8, test9, test10, test11, test12, test13, test14, test15, test16, test17, test18]

distances2 = []
snr2 = []

for test in tests2:
    test.readData()
    test.filterData()
    test.averageData()
    distances2.append(test.distance)
    snr_linear = 10 ** (test.snr_plot / 10)  # Convert dB to linear scale
    snr2.append(snr_linear.mean())

# Fit curve to the data
snr2_fit = []
index = snr2.index(max(snr2)) # Take the maximum SNR value as a reference for the fit
base_distance2 = distances2[index]
base_snr = snr2[index]
for i in range(len(snr2)):
    if i == index:
        snr2_fit.append(base_snr)
    else:
        snr2_fit.append(snr2[i]*(base_distance2/distances2[i])**4)

snr2_fit_db = 10 * np.log10(np.array(snr2_fit))  # Convert back to dB for plotting
snr2_db = 10 * np.log10(snr2)  # Convert back to dB for plotting

# Plot original data vs fitted data
plt.figure()
plt.plot(distances2, snr2_db, color='blue', label='Measured SNR')
plt.plot(distances2, snr2_fit_db, color='green', label='Fitted SNR')
plt.axhline(0,color='red', linestyle='--', label='Detection threshold')
plt.xlabel('Distance (m)')
plt.ylabel('SNR (dB)')
plt.title('SNR vs Distance')
plt.grid(True)
plt.legend()
plt.show()

# Calculate RCS vs distance

# Ideal RCS of a trihedral reflector
length = 0.14 # m
N = 1 # Correction factor
rcs_ideal = (4*np.pi*length**4)/(3*(lamb**2)) # m²

rcs2 = []

for i in range(len(distances2)):
    currentRCS2 = (snr2_fit[i]*(4*np.pi)**3*(distances2[i]**4)*k*T*B*L)/(Pt*(G**2)*(lamb**2))
    rcs2.append(currentRCS2)

# Plot RCS vs distance 
plt.figure()
plt.plot(distances2, rcs2, color = 'blue')
plt.axhline(rcs_ideal, color='red', linestyle='--', label='Ideal trihedral reflector RCS')
plt.xlabel('Distance (m)')
plt.ylabel('RCS (m²)')
#plt.ylim(0,1)
plt.grid(True)
plt.legend(loc='upper right')
plt.title('RCS vs Distance')
plt.show()

