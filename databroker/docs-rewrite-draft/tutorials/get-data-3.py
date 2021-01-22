import databroker
import matplotlib.pyplot as plt
import numpy

run = databroker.catalog['bluesky-tutorial-BMM'][23463]
ds = run.primary.read()

plt.plot(ds["dcm_energy"], numpy.log(ds["It"] / ds["I0"]))
plt.xlabel("dcm_energy")
plt.ylabel("log(It / I0)")