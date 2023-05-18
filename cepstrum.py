import numpy as np


def calculate_cepstrum(signal):
    spectrum = np.fft.fft(signal)
    log_spectrum = np.log(np.abs(spectrum) + 1e-10)
    cepstrum = np.fft.ifft(log_spectrum).real
    return cepstrum

def calculate_fundamental_frequency_cepstrum(signal, sample_rate):
    cepstrum = calculate_cepstrum(signal)
    min_freq = 50  # Hz
    max_freq = 400  # Hz
    min_index = int(sample_rate / max_freq)
    max_index = int(sample_rate / min_freq)
    peak_index = np.argmax(cepstrum[min_index:max_index]) + min_index
    fundamental_freq = sample_rate / peak_index
    return fundamental_freq
