# airSpace.py
from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport


class AirSpace:
    def __init__(self):
        self.nav_points = {}  # {number: NavPoint}
        self.nav_segments = []  # List of NavSegment
        self.nav_airports = {}  # {name: NavAirport}

    def load_from_files(self, nav_file, seg_file, airport_file):
        # Load navigation points
        with open(nav_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                number = int(parts[0])
                name = parts[1]
                lat, lon = parts[2], parts[3]
                self.nav_points[number] = NavPoint(number, name, lat, lon)

        # Load segments
        with open(seg_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                origin = int(parts[0])
                dest = int(parts[1])
                distance = float(parts[2])
                self.nav_segments.append(NavSegment(origin, dest, distance))

                # Connect points in both directions
                if origin in self.nav_points and dest in self.nav_points:
                    self.nav_points[origin].add_neighbor(self.nav_points[dest])

        # Load airports
        with open(airport_file, 'r') as f:
            current_airport = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.isupper() and len(line) == 4:  # Airport code
                    current_airport = NavAirport(line)
                    self.nav_airports[line] = current_airport
                elif line.endswith('.D'):  # SID
                    point_name = line
                    point = self.find_point_by_name(point_name)
                    if point:
                        current_airport.sids.append(point)
                elif line.endswith('.A'):  # STAR
                    point_name = line
                    point = self.find_point_by_name(point_name)
                    if point:
                        current_airport.stars.append(point)

    def find_point_by_name(self, name):
        for point in self.nav_points.values():
            if point.name == name:
                return point
        return None

    # Keep similar methods to Graph class but adapted for airspace
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
        # Similar A* implementation but using NavPoint.distance_to()
        pass