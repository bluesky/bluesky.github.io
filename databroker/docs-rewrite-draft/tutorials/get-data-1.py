import databroker

run = databroker.catalog['bluesky-tutorial-BMM'][23463]
ds = run.primary.read()
ds["I0"].plot()