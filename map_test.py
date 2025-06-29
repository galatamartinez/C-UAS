import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx

# Sample GPS points
gps_points = [
    (-3.7038, 40.4168),  # lon, lat (notice the order!)
    (-3.7040, 40.4170),
    (-3.7042, 40.4172)
]

# Create GeoDataFrame
geometry = [Point(lon, lat) for lon, lat in gps_points]
gdf = gpd.GeoDataFrame(geometry=geometry, crs="EPSG:4326")

# Project to Web Mercator (for tiles)
gdf = gdf.to_crs(epsg=3857)

# Plot
ax = gdf.plot(figsize=(8, 8), marker='o', color='red', markersize=50)
buffer = 200  # meters to zoom out from center

# Get map center
x_center, y_center = gdf.unary_union.centroid.coords[0]

# Set limits
ax.set_xlim(x_center - buffer, x_center + buffer)
ax.set_ylim(y_center - buffer, y_center + buffer)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
plt.show()