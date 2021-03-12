class Knobs:
    def __init__(self, vmSwapiness, vmDirtyBackgroundRatio, vmDirtyRatio, vmOvercommitRatio):
        self.vmSwapiness = vmSwapiness
        self.vmDirtyBackgroundRatio = vmDirtyBackgroundRatio
        self.vmDirtyRatio = vmDirtyRatio
        self.vmOvercommitRatio = vmOvercommitRatio

    def serialize(self):
        serialized = {
            'vm.swapiness' : self.vmSwapiness,
            'vm.dirty_background_ratio' : self.vmDirtyBackgroundRatio,
            'vm.dirty_ratio' : self.vmDirtyRatio,
            'vm.overcommit_ratio' : self.vmOvercommitRatio
        }
        return serialized