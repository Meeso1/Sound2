import numpy as np

WINDOW_TYPES = [
    'rectangular',
    'triangular',
    'Hanning',
    'Hamming',
    'Blackman'
]


def rectangular_window_discrete(n):
    return np.ones(n)


def triangular_window_discrete(n):
    return np.array([1 - 2*np.abs(i - (n-1)/2)/(n-1) for i in range(n)])


def hanning_window_discrete(n):
    return np.array([0.5 * (1-np.cos(2*np.pi*i/(n-1))) for i in range(n)])


def hamming_window_discrete(n):
    return np.array([0.54 - 0.46*np.cos(2*np.pi*i/(n-1)) for i in range(n)])


def blackman_window_discrete(n):
    return np.array([0.42 - 0.5*np.cos(2*np.pi*i/(n-1)) + 0.08*np.cos(4*np.pi*i/(n-1)) for i in range(n)])


def get_window(window_type: str):
    if window_type == 'rectangular':
        return rectangular_window_discrete
    elif window_type == 'triangular':
        return triangular_window_discrete
    elif window_type == 'Hanning':
        return hanning_window_discrete
    elif window_type == 'Hamming':
        return hamming_window_discrete
    elif window_type == 'Blackman':
        return blackman_window_discrete
    else:
        raise ValueError('Unknown window type')
