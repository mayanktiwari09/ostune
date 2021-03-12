class Knobs:
    def __init__(self, vmSwapiness, vmDirtyBackgroundRatio, vmDirtyRatio, vmOvercommitRatio):
        self.vmSwapiness = vmSwapiness
        self.vmDirtyBackgroundRatio = vmDirtyBackgroundRatio
        self.vmDirtyRatio = vmDirtyRatio
        self.vmOvercommitRatio = vmOvercommitRatio

    def serialize(self):
        serialized = self.serialize()
        return serialized