from oceans.filters import smoo1
import numpy as np
import matplotlib.pyplot as plt

time = np.linspace(-4, 4, 100)
series = np.sin(time)
noise_series = series + np.random.randn(len(time)) * 0.1
data_out = smoo1(series)
ws = 31
ax = plt.subplot(211)
_ = ax.plot(np.ones(ws))
windows = ["flat", "hanning", "hamming", "bartlett", "blackman"]
for w in windows[1:]:
    _ = eval("plt.plot(np." + w + "(ws) )")
_ = ax.axis([0, 30, 0, 1.1])
leg = ax.legend(windows)
_ = plt.title("The smoothing windows")
ax = plt.subplot(212)
(l1,) = ax.plot(series)
(l2,) = ax.plot(noise_series)
for w in windows:
    _ = plt.plot(smoo1(noise_series, 10, w))
l = ["original signal", "signal with noise"]
l.extend(windows)
leg = ax.legend(l)
_ = plt.title("Smoothing a noisy signal")

plt.show()