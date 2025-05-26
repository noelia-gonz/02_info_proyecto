# airSpace.py
from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport
from path import Path

class AirSpace:
    def __init__(self):
        self.nav_points = {}       # {number: NavPoint}
        self.nav_segments = []     # List of NavSegment
        self.nav_airports = {}     # {name: NavAirport}

    def load_from_files(self, nav_file, seg_file, airport_file):
        with open(nav_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                number = int(parts[0])
                name = parts[1]
                lat, lon = parts[2], parts[3]
                self.nav_points[number] = NavPoint(number, name, lat, lon)

        with open(seg_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                origin = int(parts[0])
                dest = int(parts[1])
                distance = float(parts[2])
                segment = NavSegment(origin, dest, distance)
                self.nav_segments.append(segment)

                if origin in self.nav_points and dest in self.nav_points:
                    self.nav_points[origin].add_neighbor(self.nav_points[dest])
                    self.nav_points[dest].add_neighbor(self.nav_points[origin])

        with open(airport_file, 'r') as f:
            current_airport = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.isupper() and len(line) == 4:
                    current_airport = NavAirport(line)
                    self.nav_airports[line] = current_airport
                elif line.endswith('.D'):
                    point = self.find_point_by_name(line)
                    if point:
                        current_airport.sids.append(point)
                elif line.endswith('.A'):
                    point = self.find_point_by_name(line)
                    if point:
                        current_airport.stars.append(point)

    def find_point_by_name(self, name):
        for point in self.nav_points.values():
            if point.name == name:
                return point
        return None

    def reachable_nodes(self, start_name):
        start = self.find_point_by_name(start_name)
        if not start:
            return []

        visited = []
        queue = [start]

        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.append(current)
                queue.extend(n for n in current.neighbors if n not in visited)

        return visited

    def find_shortest_path(self, origin_name, destination_name):
        origin = self.find_point_by_name(origin_name)
        destination = self.find_point_by_name(destination_name)
        if not origin or not destination:
            return None

        current_paths = [Path([origin], 0, origin.distance_to(destination))]

        while current_paths:
            current_paths.sort(key=lambda p: p.total_cost())
            current = current_paths.pop(0)
            last_node = current.last_node()

            if last_node == destination:
                return current

            for neighbor in last_node.neighbors:
                if neighbor in current.nodes:
                    continue
                cost_so_far = current.cost + last_node.distance_to(neighbor)
                estimated_remaining = neighbor.distance_to(destination)
                new_path = Path(current.nodes + [neighbor], cost_so_far, estimated_remaining)
                current_paths.append(new_path)

        return None
