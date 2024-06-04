from oceans.filters import md_trenberth
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(500)  # Time in hours.
x = 2.5 * np.sin(2 * np.pi * t / 12.42)
x += 1.5 * np.sin(2 * np.pi * t / 12.0)
x += 0.3 * np.random.randn(len(t))
filtered = md_trenberth(x)
fig, ax = plt.subplots()
(l1,) = ax.plot(t, x, label="original")
pad = [np.NaN] * 5
(l2,) = ax.plot(t, np.r_[pad, filtered, pad], label="filtered")
legend = ax.legend()
plt.show()