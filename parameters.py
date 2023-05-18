import numpy as np

from cepstrum import calculate_fundamental_frequency_cepstrum
from sound import Sound
from windows import get_window

DEFAULT_WINDOW_SIZE = 2048
BANDS = np.array([
    [0, 630],
    [630, 1720],
    [1720, 4400],
    [4400, 11025]
])


class Parameters:
    def __init__(self, window_size=DEFAULT_WINDOW_SIZE, hop_size=DEFAULT_WINDOW_SIZE // 2, window_type='rectangular'):
        self.window_size = window_size
        self.window_type = window_type
        self.hop_size = hop_size
        self.window = get_window(window_type)(window_size)
        self.cached_sound_name = None
        self.cached_volume = None
        self.cached_freq = None
        self.cached_times_window = None
        self.cached_frequency_centroid = None
        self.cached_effective_bandwidth = None
        self.cached_full_sound_spectrum = None
        self.cached_fundamental_frequency = None
        self.cached_band_energy = {}
        self.cached_band_energy_ratio = {}
        self.cached_spectral_flatness_measure = {}
        self.cached_spectral_crest_factor = {}

    def times_window(self, sound: Sound, do_slice=True):
        if not sound.path == self.cached_sound_name or self.cached_times_window is None:
            self.cached_sound_name = sound.path
            self.cached_times_window = self.calculate_times(sound)

        sound_times, _ = sound.get_selection_data()
        window_start, window_end = np.searchsorted(self.cached_times_window, sound_times[0], side="left"), np.searchsorted(self.cached_times_window, sound_times[-1], side="right")
        return self.cached_times_window[window_start:window_end] if do_slice else self.cached_times_window

    def freq(self, sound: Sound, do_slice=True):
        if not sound.path == self.cached_sound_name or self.cached_freq is None:
            self.cached_sound_name = sound.path
            self.cached_freq = self.calculate_freq(sound)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_freq[window_start:window_end] if do_slice else self.cached_freq

    def volume(self, sound: Sound, do_slice=True):
        if not sound.path == self.cached_sound_name or self.cached_volume is None:
            self.cached_sound_name = sound.path
            self.cached_volume = self.calculate_volume(sound)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_volume[window_start:window_end] if do_slice else self.cached_volume

    def frequency_centroid(self, sound: Sound, do_slice=True):
        if not sound.path == self.cached_sound_name or self.cached_frequency_centroid is None:
            self.cached_sound_name = sound.path
            self.cached_frequency_centroid = self.calculate_frequency_centroid(sound)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_frequency_centroid[window_start:window_end] if do_slice else self.cached_frequency_centroid

    def effective_bandwidth(self, sound: Sound, do_slice=True):
        if not sound.path == self.cached_sound_name or self.cached_effective_bandwidth is None:
            self.cached_sound_name = sound.path
            self.cached_effective_bandwidth = self.calculate_effective_bandwidth(sound)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_effective_bandwidth[window_start:window_end] if do_slice else self.cached_effective_bandwidth

    def band_energy(self, sound: Sound, band: int, do_slice=True):
        if not sound.path == self.cached_sound_name or band not in self.cached_band_energy:
            self.cached_sound_name = sound.path
            self.cached_band_energy[band] = self.calculate_band_energy(sound, band)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_band_energy[band][window_start:window_end] if do_slice else self.cached_band_energy[band]

    def band_energy_ratio(self, sound: Sound, band: int, do_slice=True):
        if not sound.path == self.cached_sound_name or band not in self.cached_band_energy_ratio:
            self.cached_sound_name = sound.path
            self.cached_band_energy_ratio[band] = self.calculate_band_energy_ratio(sound, band)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_band_energy_ratio[band][window_start:window_end] if do_slice else self.cached_band_energy_ratio[band]

    def spectral_flatness_measure(self, sound: Sound, band: int, do_slice=True):
        if not sound.path == self.cached_sound_name or band not in self.cached_spectral_flatness_measure:
            self.cached_sound_name = sound.path
            self.cached_spectral_flatness_measure[band] = self.calculate_spectral_flatness_measure(sound, band)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_spectral_flatness_measure[band][window_start:window_end] if do_slice else self.cached_band_energy_ratio[band]

    def spectral_crest_factor(self, sound: Sound, band: int, do_slice=True):
        if not sound.path == self.cached_sound_name or band not in self.cached_spectral_crest_factor:
            self.cached_sound_name = sound.path
            self.cached_spectral_crest_factor[band] = self.calculate_spectral_crest_factor(sound, band)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_spectral_crest_factor[band][window_start:window_end] if do_slice else self.cached_band_energy_ratio[band]

    def fundamental_frequency(self, sound: Sound, do_slice=True):
        if not sound.path == self.cached_sound_name or self.cached_fundamental_frequency is None:
            self.cached_sound_name = sound.path
            self.cached_fundamental_frequency = self.calculate_fundamental_frequency(sound)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_fundamental_frequency[window_start:window_end] if do_slice else self.cached_fundamental_frequency

    def full_sound_spectrum(self, sound: Sound):
        if not sound.path == self.cached_sound_name or self.cached_full_sound_spectrum is None:
            self.cached_sound_name = sound.path
            self.cached_full_sound_spectrum = self.calculate_full_sound_spectrum(sound)

        window_start, window_end = self.get_windowed_indexes(sound)
        return self.cached_full_sound_spectrum

    def calculate_times(self, sound: Sound):
        return np.array([sound.times[i - self.window_size] for i in range(self.window_size, sound.n_frames, self.hop_size)])

    def calculate_freq(self, sound: Sound):
        freqs = []
        for end in range(self.window_size, len(sound.sound), self.hop_size):
            start = end - self.window_size
            freqs.append(np.fft.fft(sound.sound[start:end] * self.window)[:(self.window_size // 2)])
        return np.array(np.abs(freqs))

    def calculate_volume(self, sound: Sound):
        freq = self.freq(sound, do_slice=False)
        return 1/freq.shape[1]*np.power(freq, 2).sum(axis=1)

    def calculate_frequency_centroid(self, sound: Sound):
        freq = self.freq(sound, do_slice=False)
        denominator = freq.sum(axis=1)
        return (freq * self.window_frequencies(sound)).sum(axis=1) / denominator

    def calculate_effective_bandwidth(self, sound: Sound):
        freq = self.freq(sound, do_slice=False)
        fc = self.frequency_centroid(sound, do_slice=False)
        fc = np.repeat(fc, self.window_size//2).reshape((fc.shape[0], self.window_size//2))
        return (np.power(self.window_frequencies(sound) - fc, 2)* np.power(freq,2)).sum(axis=1)/(np.power(freq,2).sum(axis=1))

    def calculate_band_energy(self, sound: Sound, band: int):
        window_frequencies = self.window_frequencies(sound)
        band_mask = np.logical_and(window_frequencies >= BANDS[band][0], window_frequencies < BANDS[band][1])
        freq = self.freq(sound, do_slice=False)
        power_spectrum = np.power(freq, 2)
        return power_spectrum[:, band_mask].sum(axis=1) # not quite sure if this denominator should be here / power_spectrum.sum(axis=1)

    def calculate_band_energy_ratio(self, sound: Sound, band: int):
        band_energy = self.band_energy(sound, band, do_slice=False)
        return band_energy / self.volume(sound, do_slice=False)

    def calculate_spectral_flatness_measure(self, sound: Sound, band: int):
        freq = self.freq(sound, do_slice=False)
        window_frequencies = self.window_frequencies(sound)
        spectrum_squared = np.power(freq, 2)
        band_mask = np.logical_and(window_frequencies >= BANDS[band][0], window_frequencies < BANDS[band][1])
        freq_dif = BANDS[band][1]- BANDS[band][0]+1
        return np.power(np.prod(spectrum_squared[:, band_mask], axis=1), 1/(freq_dif)) * freq_dif / spectrum_squared[:, band_mask].sum(axis=1)

    def calculate_spectral_crest_factor(self, sound: Sound, band: int):
        freq = self.freq(sound, do_slice=False)
        freq_squared = np.power(freq, 2)
        window_frequencies = self.window_frequencies(sound)
        band_mask = np.logical_and(window_frequencies >= BANDS[band][0], window_frequencies < BANDS[band][1])
        freq_dif = BANDS[band][1] - BANDS[band][0] + 1
        return np.argmax(freq_squared, axis=1) * freq_dif / np.sum(freq_squared[:, band_mask], axis=1)

    def calculate_fundamental_frequency(self, sound: Sound):
        fund_freqs= []
        for end in range(self.window_size, len(sound.sound), self.hop_size):
            fund_freqs.append(calculate_fundamental_frequency_cepstrum(sound.sound[end-self.window_size:end]*self.window, sound.framerate))
        return np.array(fund_freqs)

    def calculate_full_sound_spectrum(self, sound: Sound):
        return np.abs(np.fft.fft(sound.sound * get_window(self.window_type)(sound.n_frames))[:sound.n_frames // 2])


    def get_windowed_indexes(self, sound: Sound):
        sound_times, _ = sound.get_selection_data()
        times_window = self.times_window(sound, do_slice=False)
        window_start, window_end = np.searchsorted(times_window, sound_times[0],
                                                   side="left"), np.searchsorted(times_window,
                                                                                 sound_times[-1],
                                                                                 side="right")
        return window_start, window_end

    def set_window(self, window_size=None, hop_size=None, window_type=None):
        assert window_size is not None or window_type is not None, "At least one parameter must be set"
        if window_size is not None:
            self.window_size = window_size
        if window_type is not None:
            self.window_type = window_type
        if hop_size is not None:
            self.hop_size = hop_size
        self.window = get_window(self.window_type)(self.window_size)
        self.restart_cache()

    def window_frequencies(self, sound: Sound):
        return np.fft.fftfreq(self.window_size, 1 / sound.framerate)[:self.window_size // 2]

    def sound_frequencies(self, sound: Sound):
        return np.fft.fftfreq(sound.n_frames, 1 / sound.framerate)[:sound.n_frames // 2]

    def restart_cache(self):
        self.cached_sound_name = None
        self.cached_volume = None
        self.cached_freq = None
        self.cached_times_window = None
        self.cached_frequency_centroid = None
        self.cached_effective_bandwidth = None
        self.cached_full_sound_spectrum = None
        self.cached_fundamental_frequency = None
        self.cached_band_energy = {}
        self.cached_band_energy_ratio = {}
        self.cached_spectral_flatness_measure = {}
        self.cached_spectral_crest_factor = {}
