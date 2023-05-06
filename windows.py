import numpy as np


def rectangular_window_discrete(N):
    return np.ones(N)

def trinangular_window_discrete(N):
    return np.array([1 - 2*np.abs(n - (N-1)/2)/(N-1) for n in range(N)])

def hanning_window_discrete(N):
    return np.array([0.5 *(1-np.cos(2*np.pi*n/(N-1))) for n in range(N)])

def hamming_window_discrete(N):
    return np.array([0.54 - 0.46*np.cos(2*np.pi*n/(N-1)) for n in range(N)])

def blackman_window_discrete(N):
    return np.array([0.42 - 0.5*np.cos(2*np.pi*n/(N-1)) + 0.08*np.cos(4*np.pi*n/(N-1)) for n in range(N)])


def get_window(window_type: str):
    if window_type == 'rectangular':
        return rectangular_window_discrete
    elif window_type == 'triangular':
        return trinangular_window_discrete
    elif window_type == 'hanning':
        return hanning_window_discrete
    elif window_type == 'hamming':
        return hamming_window_discrete
    elif window_type == 'blackman':
        return blackman_window_discrete
    else:
        raise ValueError('Unknown window type')
