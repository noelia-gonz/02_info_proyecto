class Path:
    def __init__(self, nodes=None, cost=0.0, estimated=0.0):
        self.nodes = nodes if nodes else []
        self.cost = cost
        self.estimated = estimated
        self.segment_costs = []

    def total_cost(self):
        return self.cost + self.estimated

    def last_node(self):
        return self.nodes[-1] if self.nodes else None

    def add_node(self, node, segment_cost):
        if node is None:
            return False
        self.nodes.append(node)
        self.cost += segment_cost
        self.segment_costs.append(segment_cost)
        return True

    def ContainsNode(self, node):
        return node in self.nodes

    def CostToNode(self, node):
        if node not in self.nodes:
            return -1
        index = self.nodes.index(node)
        return sum(self.segment_costs[:index])

    def copy(self):
        new_path = Path(self.nodes.copy(), self.cost, self.estimated)
        new_path.segment_costs = self.segment_costs.copy()
        return new_path

    def __str__(self):
        if not self.nodes:
            return "Empty Path"
        return " -> ".join(n.name for n in self.nodes) + f" (Total cost: {self.cost:.2f})"

    def __repr__(self):
        return f"Path(nodes={[n.name for n in self.nodes]}, cost={self.cost:.2f}, est={self.estimated:.2f})"