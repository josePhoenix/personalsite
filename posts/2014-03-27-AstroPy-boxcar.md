---
title: Boxcar smoothing with AstroPy
excerpt: "Smooth a noisy signal by convolving it with a 'boxcar' kernel (or: the poor man's low-pass filter)"
---

# Introduction

Sometimes, when working with scientific data, you have noisy data that you need to extract low-frequency components from.

Imagine, for example, that for a project you have recorded some audio clips that have a high-frequency "hiss" artifact from your recording equipment. You can eliminate the hiss while not destroying the underlying signal that you're interested in.

![png](AstroPy_boxcar_10_1.png)

For my [current research project](http://physastro.pomona.edu/research/kapao-adaptive-optics/) on an adaptive optics instrument, we needed to smooth a signal as part of our troubleshooting process to ensure we had the pattern we expected at low frequencies.

For this, we used [IPython](http://ipython.org) (with NumPy, SciPy, Matplotlib and friends), and [AstroPy](http://astropy.org) (an up-and-coming library providing implementations of common functionality for astronomers).

# Open up IPython

The IPython notebook makes a lot of things easier, from keeping track of what you've tried to writing blog posts like this one. Open it up, and let's get started.

Bring the usual suspects (`np`, `plt`, etc.) into the namespace and tell IPython you want inline plots.

    %pylab inline

Import the convolution functionality from AstroPy.

```python
from astropy.convolution import convolve, Box1DKernel
# n.b. this overrides pylab's convolve()
```

# Create a noisy signal to smooth

```python
N = 1000 # number of samples we're dealing with
dt = 1.0 / 100.0 # 100 samples / sec
```

Create some nice random noise. By default, random noise is in the range [0.0, 1.0], so shift it down by 0.5 such that it's equal parts positive and negative.

```python
noise_ts = 3 * (np.random.rand(N) - 0.5) # center at 0
plot(timesteps, noise_ts, 'b.')
ylim(-8, 8)
```

![png](AstroPy_boxcar_3_1.png)

Now, we create our sine wave that we're going to mess up with noise.

```python
A = 5.0
frequency = 0.5 # Hz
omega = 2 * np.pi * frequency
timesteps = np.linspace(0.0, N*dt, N)
signal = A * np.sin(omega * timesteps) 
```

```python
plot(timesteps, signal)
ylim(-8, 8)
```
![png](AstroPy_boxcar_5_1.png)

Add the noise to the signal and get a much noisier wave.

```python
noisy_signal = noise_ts + signal
```

```python
plot(timesteps, noisy_signal, 'b.')
ylim(-8, 8)
```
![png](AstroPy_boxcar_7_1.png)

# Smooth the noisy signal with `convolve`

Here we're using AstroPy's `convolve` function with a "boxcar" kernel of width 10 to eliminate the high frequency noise. It's not perfect, but it's pretty good.

```python
smoothed_signal = convolve(noisy_signal, Box1DKernel(10))
```

```python
plot(timesteps, noisy_signal, 'b.', alpha=0.5, label="Noisy")
plot(timesteps, smoothed_signal, 'r', label="Smoothed")
ylim(-8, 8)
```


![png](AstroPy_boxcar_9_1.png)

Let's make the figure we had at the beginning of this post, too.

```python
figure(figsize=(12,4))
ax = subplot(121)
title("Noisy Signal")
plot(timesteps, noisy_signal)
xlim(0, 4)
subplot(122, sharey=ax)
title("Nice, Smooth Signal")
plot(timesteps, smoothed_signal, 'r', label="Smoothed")
xlim(0, 4)
```

![png](AstroPy_boxcar_10_1.png)