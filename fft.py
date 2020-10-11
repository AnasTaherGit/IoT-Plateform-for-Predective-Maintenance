import sys
import numpy as np
import pandas
from scipy import fft, signal
import matplotlib.pyplot as plt
from math import pi
from joblib import load
# path = sys.argv[1]
# print(path)

plt.title("Spectre de vibration moteur")
plt.ylabel("Acceleration (m/s²)")
plt.xlabel("frequence (Hz)")
plt.ylim((0, 1))

for path in sys.argv[1:]:
    data = pandas.read_csv(path)
    accel_x = data["Accelerometer_x"]
    accel_x_np = np.array(accel_x)
    epoch = data["localEpoch"]
    T_max = epoch[len(epoch) - 1] - epoch[0]
    # print(T_max)
    N = len(data)
    # print(N)
    t, step = np.linspace(0, T_max, len(data), retstep=True)
    # print(step)
    accel_x_np = accel_x_np - np.mean(accel_x_np)
    y_fft = fft(accel_x_np)
    y_fft_amp = 2 / N * np.abs(y_fft[0:N // 2])*9.81
    sample_freq = np.linspace(0, 1000.0 / (2.0 * step), N // 2)

    # indexes, _ = signal.find_peaks(y_fft_amp, height=0.1, distance=20)

    # for i in indexes:
    #     print("Peak :", y_fft_amp[i], "à la fréquence", sample_freq[i])
    model = load(
        "C:\\Users\\cawoo\\OneDrive\\StageLafarge\\Prototype\\model.joblib")
    X_new = np.array([y_fft_amp])
    # print(X_new.shape)
    print(model.predict(X_new)[0])
    # plt.plot(sample_freq, y_fft_amp)

# plt.show()
