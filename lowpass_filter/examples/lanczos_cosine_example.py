from oceans.filters import lanc
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(500)  # Time in hours.
h = 2.5 * np.sin(2 * np.pi * t / 12.42)
h += 1.5 * np.sin(2 * np.pi * t / 12.0)
h += 0.3 * np.random.randn(len(t))
wt = lanc(96 + 1 + 96, 1.0 / 40)
low = np.convolve(wt, h, mode="same")
high = h - low
fig, (ax0, ax1, axo) = plt.subplots(nrows=3)
ax0.plot(high, label="high")
ax1.plot(low, label="low")
axo.plot(h, label="orig")
ax0.legend(numpoints=1)
ax1.legend(numpoints=1)
axo.legend(numpoints=1)
plt.show()