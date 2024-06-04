from oceans.filters import pl33tn
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(500)  # Time in hours.
x = 2.5 * np.sin(2 * np.pi * t / 12.42)
x += 1.5 * np.sin(2 * np.pi * t / 12.0)
x += 0.3 * np.random.randn(len(t))
filtered_33 = pl33tn(x, dt=4.0)  # 33 hr filter
filtered_33d3 = pl33tn(x, dt=4.0, T=72.0)  # 3 day filter
fig, ax = plt.subplots()
(l1,) = ax.plot(t, x, label="original")
pad = [np.NaN] * 8
(l2,) = ax.plot(t, np.r_[pad, filtered_33, pad], label="33 hours")
pad = [np.NaN] * 17
(l3,) = ax.plot(t, np.r_[pad, filtered_33d3, pad], label="3 days")
legend = ax.legend()
plt.show()