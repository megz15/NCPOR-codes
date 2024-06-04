from oceans.filters import fft_lowpass
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(500)  # Time in hours.
x = 2.5 * np.sin(2 * np.pi * t / 12.42)
x += 1.5 * np.sin(2 * np.pi * t / 12.0)
x += 0.3 * np.random.randn(len(t))
filtered = fft_lowpass(x, low=1 / 30, high=1 / 40)
fig, ax = plt.subplots()
(l1,) = ax.plot(t, x, label="original")
(l2,) = ax.plot(t, filtered, label="filtered")
legend = ax.legend()
plt.show()