from node import Node
class Segment:
    def __init__(self, name, origin, destination):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.cost = self.calculate_cost()

    def calculate_cost(self):
        return ((self.origin.x - self.destination.x) ** 2 +(self.origin.y - self.destination.y) ** 2) ** 0.5

    def __str__(self):
        return "Segment '{}': {} -> {}, cost: {:.2f}".format(
            self.name,
            self.origin.name,
            self.destination.name,
            self.cost)

    def __repr__(self):
        return "Segment(name='{}', origin='{}', destination='{}', cost={:.2f})".format(self.name,self.origin.name,self.destination.name,self.cost)