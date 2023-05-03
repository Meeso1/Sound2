import numpy as np

from sound import Sound


class Parameters:
    def __init__(self):
        self.cached_sound_name = None
        self.cached_volume = None

    def volume(self, sound):
        if not sound.path == self.cached_sound_name:
            self.cached_sound_name = sound.path
            self.cached_volume = self.calculate_volume(sound)

        return self.cached_volume[sound.selection_start_index:sound.selection_end_index]

    @staticmethod
    def calculate_volume(sound):
        volume = np.square(sound.sound)
        max_volume = volume.max()
        return volume / max_volume

