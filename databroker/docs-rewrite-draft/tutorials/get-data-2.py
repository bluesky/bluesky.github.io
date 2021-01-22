import databroker

run = databroker.catalog['bluesky-tutorial-BMM'][23463]
ds = run.primary.read()

# The plot accessor on xarray.Dataset
ds.plot.scatter(x="dcm_energy", y="I0")