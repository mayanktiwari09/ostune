class Metrics:
    def __init__(self, throughput):
        self.throughput = throughput

    def serialize(self):
        serialized = {'throughput': self.throughput}
        return serialized