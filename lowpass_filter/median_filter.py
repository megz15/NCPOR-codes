from oceans.filters import medfilt1
import matplotlib.pyplot as plt
import numpy as np

# 100 pseudo-random integers ranging from 1 to 100, plus three large

# outliers for illustration.

x = np.r_[

    np.ceil(np.random.rand(25) * 100),

    [1000],

    np.ceil(np.random.rand(25) * 100),

    [2000],

    np.ceil(np.random.rand(25) * 100),

    [3000],

    np.ceil(np.random.rand(25) * 100),

]

L = 2

xout = medfilt1(x=x, L=L)

ax = plt.subplot(211)

l1, l2 = ax.plot(x), ax.plot(xout)

ax.grid(True)

y1min, y1max = np.min(xout) * 0.5, np.max(xout) * 2.0

leg1 = ax.legend(["x (pseudo-random)", "xout"])

t1 = ax.set_title(

    '''Median filter with window length %s.

                  Removes outliers, tracks remaining signal)'''

    % L

)

L = 103

xout = medfilt1(x=x, L=L)

ax = plt.subplot(212)

(l1, l2,) = ax.plot(

    x

), ax.plot(xout)

ax.grid(True)

y2min, y2max = np.min(xout) * 0.5, np.max(xout) * 2.0

leg2 = ax.legend(["Same x (pseudo-random)", "xout"])

t2 = ax.set_title(

    '''Median filter with window length %s.

                  Removes outliers and noise'''

    % L

)

ax = plt.subplot(211)

lims1 = ax.set_ylim([min(y1min, y2min), max(y1max, y2max)])

ax = plt.subplot(212)

lims2 = ax.set_ylim([min(y1min, y2min), max(y1max, y2max)])

plt.show()