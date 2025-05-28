<<<<<<< HEAD
from node import Distance


class Path:
    def __init__(self, start_node=None):
        """
        Inicializa un nuevo camino
        Args:
            start_node: Nodo inicial del camino (opcional)
        """
        self.nodes = [start_node] if start_node else []
        self.cost = 0.0  # Coste acumulado del camino
        self.segment_costs = []  # Costes individuales de cada segmento

    def AddNodeToPath(self, node, segment_cost):
        """
        Añade un nodo al final del camino
        Args:
            node: Nodo a añadir
            segment_cost: Coste del segmento que lleva a este nodo
        Returns:
            True si se añadió el nodo, False si no
        """
        if node is None:
            return False

        if not self.nodes:
            # Camino vacío, podemos añadir sin verificar conexión
            self.nodes.append(node)
            self.cost += segment_cost
            self.segment_costs.append(segment_cost)
            return True

        # Verificar que el nuevo nodo es vecino del último nodo del camino
        if node in self.nodes[-1].neighbors:
            self.nodes.append(node)
            self.cost += segment_cost
            self.segment_costs.append(segment_cost)
            return True

        return False

    def ContainsNode(self, node):
        """
        Comprueba si un nodo está en el camino
        Args:
            node: Nodo a buscar
        Returns:
            True si el nodo está en el camino, False si no
        """
        return node in self.nodes

    def CostToNode(self, node):
        """
        Calcula el coste acumulado hasta un nodo específico del camino
        Args:
            node: Nodo hasta el que calcular el coste
        Returns:
            Coste acumulado o -1 si el nodo no está en el camino
        """
        if node not in self.nodes:
            return -1

=======
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
>>>>>>> v3-dev2
        index = self.nodes.index(node)
        return sum(self.segment_costs[:index])

    def copy(self):
<<<<<<< HEAD
        """
        Crea una copia exacta de este camino
        Returns:
            Nuevo objeto Path idéntico a este
        """
        new_path = Path()
        new_path.nodes = self.nodes.copy()
        new_path.cost = self.cost
        new_path.segment_costs = self.segment_costs.copy()
        return new_path

    def PlotPath(self, graph, ax):
        """
        Dibuja el camino en un gráfico matplotlib
        Args:
            graph: Grafo al que pertenece el camino
            ax: Ejes matplotlib donde dibujar
        """
        if len(self.nodes) < 2:
            return

        for i in range(len(self.nodes) - 1):
            n1, n2 = self.nodes[i], self.nodes[i + 1]

            # Dibujar segmento
            ax.plot([n1.x, n2.x], [n1.y, n2.y], 'r-', linewidth=2)

            # Mostrar coste del segmento
            mid_x = (n1.x + n2.x) / 2
            mid_y = (n1.y + n2.y) / 2
            cost = self.segment_costs[i]
            ax.text(mid_x, mid_y, f"{cost:.1f}",
                    color='red', ha='center', va='center',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

    def __str__(self):
        """Representación del camino como cadena de texto"""
=======
        new_path = Path(self.nodes.copy(), self.cost, self.estimated)
        new_path.segment_costs = self.segment_costs.copy()
        return new_path

    def __str__(self):
>>>>>>> v3-dev2
        if not self.nodes:
            return "Empty Path"
        return " -> ".join(n.name for n in self.nodes) + f" (Total cost: {self.cost:.2f})"

    def __repr__(self):
<<<<<<< HEAD
        """Representación formal del objeto"""
        return f"Path(nodes={[n.name for n in self.nodes]}, cost={self.cost:.2f})"
=======
        return f"Path(nodes={[n.name for n in self.nodes]}, cost={self.cost:.2f}, est={self.estimated:.2f})"
>>>>>>> v3-dev2
