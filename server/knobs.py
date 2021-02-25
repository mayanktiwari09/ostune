class Knobs:
    def __init__(self, vmSwapiness):
        self.vmSwapiness = vmSwapiness

    def serialize(self):
        return {
            'vm.Swapiness': self.vmSwapiness
        }