import numpy as np
from scipy.io import wavfile


class Sound:
    def __init__(self, path):
        self.path = path
        self.framerate, sound = wavfile.read(path)
        if sound.ndim > 1:
            sound = sound[:, 0]

        self.sound = self.normalize(sound)
        self.n_frames = len(self.sound)
        self.duration = self.n_frames / self.framerate
        self.times = self.get_times(self.framerate, self.n_frames)

        self.selection_start_index = 0
        self.selection_end_index = self.n_frames - 1

    @staticmethod
    def normalize(sound):
        return sound / sound.max()

    @staticmethod
    def get_times(framerate, length):
        step = 1 / framerate
        return np.array([i * step for i in range(length)])

    def select(self, start_time, end_time):
        start = int(start_time * self.framerate)
        end = int(np.ceil(end_time * self.framerate))

        self.selection_start_index = start if start > 0 else 0
        self.selection_end_index = end if end < self.n_frames else (self.n_frames - 1)

    def shift_right(self, step=0.1):
        diff = self.selection_end_index - self.selection_start_index
        shift = int(diff * step) if int(diff * step) > 0 else 1

        end = self.selection_end_index + shift
        self.selection_end_index = end if end < self.n_frames else (self.n_frames - 1)
        self.selection_start_index = self.selection_end_index - diff

    def shift_left(self, step=0.1):
        diff = self.selection_end_index - self.selection_start_index
        shift = int(diff * step) if int(diff * step) > 0 else 1

        start = self.selection_start_index - shift
        self.selection_start_index = start if start > 0 else 0
        self.selection_end_index = self.selection_start_index + diff

    def reset(self):
        self.selection_start_index = 0
        self.selection_end_index = self.n_frames - 1

    def get_selection_data(self):
        return self.times[self.selection_start_index:self.selection_end_index], \
               self.sound[self.selection_start_index:self.selection_end_index]
