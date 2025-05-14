
class NavPoint:
    def __init__(self, number, name, latitude, longitude):
        self.number = number
        self.name = name
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.neighbors = []  # List of connected NavPoints

    def add_neighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            return True
        return False

    def distance_to(self, other):
        # Haversine formula for great-circle distance
        from math import radians, sin, cos, sqrt, atan2
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return 6371 * c  # Earth radius in km