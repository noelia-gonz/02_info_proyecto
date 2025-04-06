import matplotlib.pyplot as plt
from node import Node

class Graph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def connect(self, name1, name2):
        node1 = self.get_node_by_name(name1)
        node2 = self.get_node_by_name(name2)
        if node1 and node2 and node2 not in node1.neighbors:
            node1.neighbors.append(node2)

    def get_node_by_name(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None
#Guardar los datos del grafico como file.txt
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(f"{len(self.nodes)}\n")
            for node in self.nodes:
                f.write(f"{node.name} {node.x} {node.y}\n")
            edges = []
            for node in self.nodes:
                for neighbor in node.neighbors:
                    edges.append((node.name, neighbor.name))
            f.write(f"{len(edges)}\n")
            for edge in edges:
                f.write(f"{edge[0]} {edge[1]}\n")

#Cargar data desde archivo
    @staticmethod
    def load_from_file(filename):
        G = Graph()
        with open(filename, 'r') as f:
            lines = f.readlines()
        n_nodes = int(lines[0])
        nodes_data = []
        for i in range(1, n_nodes + 1):
            node_name, x, y = lines[i].split()
            nodes_data.append((node_name, float(x), float(y)))
        G.nodes = [Node(name, x, y) for name, x, y in nodes_data]

        n_edges = int(lines[n_nodes + 1])
        for i in range(n_nodes + 2, n_nodes + 2 + n_edges):
            name1, name2 = lines[i].split()
            G.connect(name1, name2)
        return G
#Encontrar punto mas cerca:)
    def closest(self, x, y):
        min_dist = float('inf')
        closest_node = None
        for node in self.nodes:
            dist = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        return closest_node

    def draw(self, focus=None):
        plt.figure(figsize=(8, 6))

        # segmentos
        for node in self.nodes:
            for neighbor in node.neighbors:
                plt.plot([node.x, neighbor.x], [node.y, neighbor.y], 'gray')  # Líneas grises para los segmentos

        # puntos
        for node in self.nodes:
            color = 'blue' if focus and node.name == focus else 'black'  # Resalta el nodo si es el foco
            plt.plot(node.x, node.y, 'o', color=color, markersize=10)
            plt.text(node.x, node.y + 0.3, node.name, ha='center')

        plt.grid(True)
        plt.title(focus if focus else "Full Graph")
        plt.show()

