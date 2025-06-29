import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import plotly.express as px

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
        self.noise = 10 * np.log10(self.data.noise) # Convert to dB
    
    # Filtering for INDOORS tests (mostly 2D surfaces)
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

    # Filtering for OUTDOORS tests (3D surfaces)
    def filterDataOutdoors(self, l, w, h, threshold):

        # Given drone principal dimensions (length, width, height), filter data with a sphere
        # Center position will be stablished around the measured distance

        if self.axis == 'x':
            xc = self.distance + l/2
            yc = 0
            zc = 0
        elif self.axis == 'y':
            xc = 0
            yc = self.distance + l/2
            zc = 0
        elif self.axis == 'z':
            xc = 0
            yc = 0
            zc = self.distance + l/2

        # Define sphere radius (higher dimension of the drone + margin)
        self.r = max(l, w, h)*(1 + threshold)

        # Calculate distance to the center and filter data
        dist = np.sqrt((self.x - xc)**2 + (self.y -yc)**2 + (self.z - zc)**2)
        inside_sphere = dist <= self.r

        self.filteredData = self.data[inside_sphere]
        
    def averageData(self):

        self.snr = 10 * np.log10(self.filteredData.snr) # Convert to dB
        snr_avg = self.snr.groupby(self.cycle).mean()
        self.snr_plot = snr_avg.values
        self.cycle_plot = snr_avg.index.values

    def plotData(self):
        plt.plot(self.cycle_plot, self.snr_plot)

    def dataMetrics(self):

        # Compare gross vs filtered nº of points
        self.gross_points = len(self.data)
        self.filtered_points = len(self.filteredData)
        self.ratio = self.filtered_points / self.gross_points
        print(f"Test: {self.testname}")
        print(f"Filtered/Gross point ratio: {self.ratio}")

    def selectPointClouds(self):

        # Select the point clouds for each test with the highest number of points
        cycle_counts = self.data.groupby('cycle').size()
        cycle_countsf = self.filteredData.groupby('cycle').size()
        max_cycle = cycle_counts.idxmax()
        max_cyclef = cycle_countsf.idxmax()

        self.dataPlot = self.filteredData[self.filteredData.cycle == max_cycle]
        self.dataCompare = self.data[self.data.cycle == max_cyclef]

    # ONLY FOR 2D SURFACES
    def rotateData(self):

        # Rotate points 90º counterclockwise around x axis
        self.x_rot = self.filteredData.x
        self.y_rot = self.filteredData.z
        self.z_rot = -self.filteredData.y

        self.x_plot = self.dataPlot.x
        self.y_plot = self.dataPlot.z
        self.z_plot = -self.dataPlot.y

        self.x_compare = self.dataCompare.x
        self.y_compare = self.dataCompare.z
        self.z_compare = -self.dataCompare.y

    # ONLY FOR 2D SURFACES
    def plotPointCloud(self):
        
        # Plot point cloud        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.x_plot, self.y_plot, self.z_plot, c='b', marker='o')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim(-0.5,0.5)
        ax.set_ylim(-0.5,0.5)
        ax.set_zlim(-2,2)
        ax.set_title(self.testname)

        # Draw 3D rectangle (representing floor)
        verts = [(-0.5,-0.5,-self.distance), (0.5,-0.5,-self.distance), (0.5,0.5,-self.distance), (-0.5,0.5,-self.distance)]
        rect = Poly3DCollection([verts], facecolor = 'yellow', alpha = 0.2)
        ax.add_collection3d(rect)

    def plotOutdoorsData(self):

        # Plot point cloud
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # CONSIDER PLOTTING ROTATED DATA IN THIS METHOD
        ax.scatter(self.filteredData.x, self.filteredData.y, self.filteredData.z)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim(-0.5*self.r,0.5*self.r)
        ax.set_ylim(-0.5*self.r,0.5*self.r)
        ax.set_zlim(-0.5*self.r,0.5*self.r)
        ax.set_title(self.testname)

        # Draw sphere
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = self.r * np.outer(np.cos(u), np.sin(v))
        y = self.r * np.outer(np.sin(u), np.sin(v))
        z = self.r * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color='red', alpha = 0.2, edgecolor = 'black')
        
        plt.show()


    def savePointCloud(self):

        # Save figure to html format
        df = pd.DataFrame({'x': self.x_rot, 'y': self.y_rot, 'z': self.z_rot})
        fig = px.scatter_3d(df, x='x', y='y', z='z')
        fig.write_html(f"{self.testname}.html")

    