import databroker
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

run = databroker.catalog['bluesky-tutorial-RSOXS']['777b44a']
corrected = run.primary.to_dask()["Synced_waxs_image"] - run.dark.to_dask()["Synced_waxs_image"].mean("time")
middle_image = corrected[64, 0, :, :]  # Pull out a 2D slice.
plt.imshow(middle_image, norm=LogNorm(), origin='lower')