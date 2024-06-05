import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
N = 50

for alpha in [0.64, 2.55, 7.64, 31.83]:
    ax.plot(signal.windows.kaiser_bessel_derived(2*N, np.pi*alpha),
            label=f"{alpha=}")

ax.grid(True)
ax.set_title("Kaiser-Bessel derived window")
ax.set_ylabel("Amplitude")
ax.set_xlabel("Sample")
ax.set_xticks([0, N, 2*N-1])
ax.set_xticklabels(["0", "N", "2N+1"])  
ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.707, 0.8, 1.0])

fig.legend(loc="center")
fig.tight_layout()
fig.show()
plt.show()