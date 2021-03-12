from constants import *

class Metrics:
    def __init__(self, throughput):
        self.throughput = throughput

    def serialize(self):
        serialized = {THROUGHPUT: self.throughput}
        return serialized