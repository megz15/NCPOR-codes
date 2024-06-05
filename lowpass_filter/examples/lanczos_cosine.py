import matplotlib.pyplot as plt
import numpy as np

def lanc(numwt, haf):
    """
    Generates a numwt + 1 + numwt lanczos cosine low pass filter with -6dB
    (1/4 power, 1/2 amplitude) point at haf

    Parameters
    ----------
    numwt : int
            number of points
    haf : float
            frequency (in 'cpi' of -6dB point, 'cpi' is cycles per interval.
            For hourly data cpi is cph,
    """
    summ = 0
    numwt += 1
    wt = np.zeros(numwt)

    # Filter weights.
    ii = np.arange(numwt)
    wt = 0.5 * (1.0 + np.cos(np.pi * ii * 1.0 / numwt))
    ii = np.arange(1, numwt)
    xx = np.pi * 2 * haf * ii
    wt[1 : numwt + 1] = wt[1 : numwt + 1] * np.sin(xx) / xx
    summ = wt[1 : numwt + 1].sum()
    xx = wt.sum() + summ
    wt /= xx
    return np.r_[wt[::-1], wt[1 : numwt + 1]]

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