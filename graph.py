import matplotlib.pyplot as plt
from node import Node, Distance
from path import Path
import heapq


class Graph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        """Añade un nodo al grafo si no existe ya"""
        if not any(n.name == node.name for n in self.nodes):
            self.nodes.append(node)
            return True
        return False

    def connect(self, name1, name2):
        """Conecta dos nodos por nombre"""
        node1 = self.get_node_by_name(name1)
        node2 = self.get_node_by_name(name2)
        if node1 and node2 and node2 not in node1.neighbors:
            node1.neighbors.append(node2)
            return True
        return False

    def get_node_by_name(self, name):
        """Obtiene un nodo por su nombre"""
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def reachable_nodes(self, start_name):
        """
        Devuelve todos los nodos alcanzables desde start_name usando BFS
        Args:
            start_name: nombre del nodo de inicio
        Returns:
            Lista de nodos alcanzables o lista vacía si no se encuentra el nodo inicial
        """
        start_node = self.get_node_by_name(start_name)
        if not start_node:
            return []

        visited = []
        queue = [start_node]

        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.append(current)
                # Añadir vecinos no visitados
                queue.extend(neighbor for neighbor in current.neighbors
                             if neighbor not in visited)

        return visited

    def FindShortestPath(self, origin_name, destination_name):
        """
        Implementación del algoritmo A* para encontrar el camino más corto
        Args:
            origin_name: nombre del nodo de origen
            destination_name: nombre del nodo de destino
        Returns:
            Objeto Path con el camino más corto o None si no hay camino
        """
        origin = self.get_node_by_name(origin_name)
        destination = self.get_node_by_name(destination_name)

        if not origin or not destination:
            return None

        # Cola de prioridad: (f_cost, g_cost, path)
        open_set = []
        heapq.heappush(open_set, (0, 0, Path(origin)))

        closed_set = set()

        while open_set:
            _, g_cost, current_path = heapq.heappop(open_set)
            current_node = current_path.nodes[-1]

            # Si llegamos al destino
            if current_node == destination:
                return current_path

            if current_node in closed_set:
                continue
            closed_set.add(current_node)

            # Explorar vecinos
            for neighbor in current_node.neighbors:
                if neighbor in closed_set:
                    continue

                # Calcular coste real hasta el vecino
                segment_cost = Distance(current_node, neighbor)
                new_g_cost = g_cost + segment_cost

                # Heurística (distancia euclídea al destino)
                h_cost = Distance(neighbor, destination)

                # Crear nuevo camino
                new_path = current_path.copy()
                new_path.AddNodeToPath(neighbor, segment_cost)

                # Añadir a la cola de prioridad
                heapq.heappush(open_set, (new_g_cost + h_cost, new_g_cost, new_path))

        return None  # No se encontró camino

    def save_to_file(self, filename):
        """Guarda el grafo en un archivo de texto"""
        with open(filename, 'w') as f:
            # Escribir nodos
            f.write(f"{len(self.nodes)}\n")
            for node in self.nodes:
                f.write(f"{node.name} {node.x} {node.y}\n")

            # Escribir conexiones
            edges = []
            for node in self.nodes:
                for neighbor in node.neighbors:
                    edges.append((node.name, neighbor.name))

            f.write(f"{len(edges)}\n")
            for edge in edges:
                f.write(f"{edge[0]} {edge[1]}\n")

    @staticmethod
    def load_from_file(filename):
        """Carga un grafo desde archivo"""
        G = Graph()
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Leer nodos
        n_nodes = int(lines[0])
        for i in range(1, n_nodes + 1):
            node_name, x, y = lines[i].split()
            G.add_node(Node(node_name, float(x), float(y)))

        # Leer conexiones
        n_edges = int(lines[n_nodes + 1])
        for i in range(n_nodes + 2, n_nodes + 2 + n_edges):
            name1, name2 = lines[i].split()
            G.connect(name1, name2)

        return G

    def closest(self, x, y):
        """Encuentra el nodo más cercano a las coordenadas (x,y)"""
        min_dist = float('inf')
        closest_node = None

        for node in self.nodes:
            dist = Distance(node, Node('temp', x, y))
            if dist < min_dist:
                min_dist = dist
                closest_node = node

        return closest_node

    def draw(self, focus=None):
        """Dibuja el grafo usando matplotlib (para pruebas)"""
        plt.figure(figsize=(8, 6))

        # Dibujar conexiones
        for node in self.nodes:
            for neighbor in node.neighbors:
                plt.plot([node.x, neighbor.x], [node.y, neighbor.y], 'gray')

        # Dibujar nodos
        for node in self.nodes:
            color = 'blue' if focus and node.name == focus else 'black'
            plt.plot(node.x, node.y, 'o', color=color, markersize=10)
            plt.text(node.x, node.y + 0.3, node.name, ha='center')

        plt.grid(True)
        plt.title(focus if focus else "Grafo completo")
        plt.show()

