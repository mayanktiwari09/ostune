from constants import *

class Knobs:
    def __init__(self, vmSwapiness, vmDirtyBackgroundRatio, vmDirtyRatio, vmOvercommitRatio):
        self.vmSwapiness = vmSwapiness
        self.vmDirtyBackgroundRatio = vmDirtyBackgroundRatio
        self.vmDirtyRatio = vmDirtyRatio
        self.vmOvercommitRatio = vmOvercommitRatio

    def serialize(self):
        serialized = {
            VM_SWAPINESS : self.vmSwapiness,
            VM_DIRTY_BACKGROUND_RATIO : self.vmDirtyBackgroundRatio,
            VM_DIRTY_RATIO : self.vmDirtyRatio,
            VM_OVERCOMMIT_RATIO : self.vmOvercommitRatio
        }
        return serialized