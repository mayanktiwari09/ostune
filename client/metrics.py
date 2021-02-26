class Metrics:
    def __init__(self, throughput):
        self.throughput = throughput

    def serialize(self):
        return {
            'throughput': self.throughput
        }
