import random
from functools import partial
import json

import numpy as np
import torch

from ops.audio import read_audio, compute_stft, trim_audio


class MapLabels:

    def __init__(self, class_map, drop_raw=True):

        self.class_map = class_map

    def __call__(self, dataset, **inputs):

        labels = np.zeros(len(self.class_map), dtype=np.float32)
        for c in inputs["raw_labels"]:
            labels[self.class_map[c]] = 1.0

        transformed = dict(inputs)
        transformed["labels"] = labels
        transformed.pop("raw_labels")

        return transformed


class LoadAudio:

    def __init__(self):

        pass

    def __call__(self, dataset, **inputs):

        audio, sr = read_audio(inputs["filename"])

        transformed = dict(inputs)
        transformed["audio"] = audio
        transformed["sr"] = sr

        return transformed


class STFT:

    def __init__(self, n_fft, hop_size):

        self.n_fft = n_fft
        self.hop_size = hop_size

    def __call__(self, dataset, **inputs):

        stft = compute_stft(
            inputs["audio"], window_size=self.n_fft, hop_size=self.hop_size)

        transformed = dict(inputs)
        transformed["stft"] = stft

        return transformed


class OneOf:

    def __init__(self, transforms):

        self.transforms = transforms

    def __call__(self, dataset, **inputs):

        transform = random.choice(self.transforms)
        return transform(**inputs)


class DropFields:

    def __init__(self, fields):

        self.to_drop = fields

    def __call__(self, dataset, **inputs):

        transformed = dict()

        for name, input in inputs.items():
            if not name in self.to_drop:
                transformed[name] = input

        return transformed


class Compose:

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, dataset=None, **inputs):
        for t in self.transforms:
            inputs = t(dataset=dataset, **inputs)

        return inputs