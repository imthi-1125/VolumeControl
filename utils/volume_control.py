# utils/volume_control.py
import os
import numpy as np

class VolumeController:
    def __init__(self, minDist=30, maxDist=300):
        self.minDist = minDist
        self.maxDist = maxDist

    def distance_to_percent(self, distance):
        if self.maxDist == self.minDist:
            return 0
        percent = int(np.clip(np.interp(distance, [self.minDist, self.maxDist], [0, 100]), 0, 100))
        return percent

    def set_volume_percent(self, percent):
        percent = int(np.clip(percent, 0, 100))
        os.system(f"osascript -e 'set volume output volume {percent}'")

    def set_mute(self, mute=True):
        if mute:
            os.system("osascript -e 'set volume output muted true'")
        else:
            os.system("osascript -e 'set volume output muted false'")
