import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

filename = 'test_1.csv'
data = pd.read_csv(filename)

cycle = data.cycle
object = data.object
snr = 10 * np.log10(data.snr)

# Average the SNR for each cycle
snr_avg = snr.groupby(cycle).mean()
snr_plot = snr_avg.values
cycle_plot = snr_avg.index.values

# Rectangles to separate reflectivity values
low_rect = patches.Rectangle((1,0), 19, 10, facecolor = 'red', alpha = 0.2)
medium_rect = patches.Rectangle((1,10), 19, 10, facecolor = 'orange', alpha = 0.2)
high_rect = patches.Rectangle((1,20), 19, 10, facecolor = 'green', alpha = 0.2)

# Plot values
fig, ax = plt.subplots(figsize = (9, 6))
plt.plot(cycle_plot, snr_plot)
ax.add_patch(low_rect)
ax.add_patch(medium_rect)
ax.add_patch(high_rect)
plt.xlabel('Cycle')
plt.ylabel('SNR (dB)')
plt.legend(['Test 1'], loc = 'upper right')
plt.text(10, 5, 'Low reflectivity', ha='center', va='center', fontsize = 10, color = 'red')
plt.text(10, 15, 'Medium reflectivity', ha='center', va='center', fontsize = 10, color = 'orange')
plt.text(10, 25, 'High reflectivity', ha='center', va='center', fontsize = 10, color = 'green')
plt.xticks(cycle_plot)
plt.tick_params(axis='x', which = 'both', labelsize = 10, pad = 12)
plt.show()