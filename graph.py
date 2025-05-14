import heapq
from path import Path
from airSpace import AirSpace  # New for Version 3
from node import Node, Distance


class Graph:
    def __init__(self):
        self.nodes = []  # For simple graph mode
        self.airspace = None  # For airspace mode (Version 3)
        self.mode = "graph"  # 'graph' or 'airspace'

    # --------------------------
    # Original Graph Methods (V1-V2)
    # --------------------------

    def add_node(self, node):
        """Add node to graph (graph mode only)"""
        if self.mode != "graph":
            raise ValueError("Cannot add nodes in airspace mode")
        if not any(n.name == node.name for n in self.nodes):
            self.nodes.append(node)
            return True
        return False

    def connect(self, name1, name2):
        """Connect two nodes by name (graph mode only)"""
        if self.mode != "graph":
            raise ValueError("Cannot connect nodes in airspace mode")
        node1 = self.get_node_by_name(name1)
        node2 = self.get_node_by_name(name2)
        if node1 and node2 and node2 not in node1.neighbors:
            node1.neighbors.append(node2)
            return True
        return False

    def get_node_by_name(self, name):
        """Get node by name (works in both modes)"""
        if self.mode == "airspace" and self.airspace:
            return self.airspace.find_point_by_name(name)
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def reachable_nodes(self, start_name):
        """Get all reachable nodes from start node (works in both modes)"""
        if self.mode == "airspace" and self.airspace:
            return self.airspace.reachable_nodes(start_name)

        start_node = self.get_node_by_name(start_name)
        if not start_node:
            return []

        visited = []
        queue = [start_node]

        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.append(current)
                queue.extend(neighbor for neighbor in current.neighbors
                             if neighbor not in visited)
        return visited

    def FindShortestPath(self, origin_name, destination_name):
        """Find shortest path using A* (works in both modes)"""
        if self.mode == "airspace" and self.airspace:
            return self.airspace.find_shortest_path(origin_name, destination_name)

        origin = self.get_node_by_name(origin_name)
        destination = self.get_node_by_name(destination_name)

        if not origin or not destination:
            return None

        # Priority queue: (f_cost, g_cost, path)
        open_set = []
        heapq.heappush(open_set, (0, 0, Path(origin)))

        closed_set = set()

        while open_set:
            _, g_cost, current_path = heapq.heappop(open_set)
            current_node = current_path.nodes[-1]

            if current_node == destination:
                return current_path

            if current_node in closed_set:
                continue
            closed_set.add(current_node)

            for neighbor in current_node.neighbors:
                if neighbor in closed_set:
                    continue

                segment_cost = Distance(current_node, neighbor)
                new_g_cost = g_cost + segment_cost
                h_cost = Distance(neighbor, destination)

                new_path = current_path.copy()
                new_path.AddNodeToPath(neighbor, segment_cost)

                heapq.heappush(open_set, (new_g_cost + h_cost, new_g_cost, new_path))

        return None

    def closest(self, x, y):
        """Find closest node to coordinates (works in both modes)"""
        if self.mode == "airspace" and self.airspace:
            if not self.airspace.nav_points:
                return None
            # Convert x,y to lon,lat for airspace mode
            from navPoint import NavPoint
            temp_point = NavPoint(0, "temp", y, x)  # Note: lat=y, lon=x
            closest = None
            min_dist = float('inf')
            for point in self.airspace.nav_points.values():
                dist = point.distance_to(temp_point)
                if dist < min_dist:
                    min_dist = dist
                    closest = point
            return closest

        min_dist = float('inf')
        closest_node = None
        temp_node = Node('temp', x, y)

        for node in self.nodes:
            dist = Distance(node, temp_node)
            if dist < min_dist:
                min_dist = dist
                closest_node = node

        return closest_node

    # --------------------------
    # New Airspace Methods (V3)
    # --------------------------

    def load_airspace(self, nav_file, seg_file, airport_file):
        """Load airspace data from files"""
        self.airspace = AirSpace()
        self.airspace.load_from_files(nav_file, seg_file, airport_file)
        self.mode = "airspace"
        return True

    def save_to_file(self, filename):
        """Save graph to file (graph mode only)"""
        if self.mode != "graph":
            raise ValueError("Cannot save airspace data in graph format")
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

    @staticmethod
    def load_from_file(filename):
        """Load graph from file (graph mode only)"""
        G = Graph()
        with open(filename, 'r') as f:
            lines = f.readlines()

        n_nodes = int(lines[0])
        for i in range(1, n_nodes + 1):
            node_name, x, y = lines[i].split()
            G.add_node(Node(node_name, float(x), float(y)))

        n_edges = int(lines[n_nodes + 1])
        for i in range(n_nodes + 2, n_nodes + 2 + n_edges):
            name1, name2 = lines[i].split()
            G.connect(name1, name2)

        return G

    # --------------------------
    # Visualization Methods
    # --------------------------

    def draw(self, focus=None):
        """Draw the graph (simple version for testing)"""
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 8))

        if self.mode == "airspace" and self.airspace:
            # Draw airspace
            for segment in self.airspace.nav_segments:
                origin = self.airspace.nav_points.get(segment.origin_number)
                dest = self.airspace.nav_points.get(segment.destination_number)
                if origin and dest:
                    plt.plot([origin.longitude, dest.longitude],
                             [origin.latitude, dest.latitude], 'gray')

            for point in self.airspace.nav_points.values():
                color = 'blue' if focus and point.name == focus else 'black'
                plt.plot(point.longitude, point.latitude, 'o', color=color)
                plt.text(point.longitude, point.latitude + 0.1, point.name, ha='center')

            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
        else:
            # Draw simple graph
            for node in self.nodes:
                for neighbor in node.neighbors:
                    plt.plot([node.x, neighbor.x], [node.y, neighbor.y], 'gray')

            for node in self.nodes:
                color = 'blue' if focus and node.name == focus else 'black'
                plt.plot(node.x, node.y, 'o', color=color)
                plt.text(node.x, node.y + 0.3, node.name, ha='center')

            plt.xlabel("X Coordinate")
            plt.ylabel("Y Coordinate")

        plt.grid(True)
        plt.title("Airspace" if self.mode == "airspace" else "Graph")
        plt.show()