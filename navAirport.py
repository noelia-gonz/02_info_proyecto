
class NavAirport:
    def __init__(self, name,latitude=None, longitude=None):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.sids = []  # List of NavPoints for departures
        self.stars = []  # List of NavPoints for arrivals

    def add_sid(self, nav_point):
        if nav_point not in self.sids:
            self.sids.append(nav_point)

    def add_star(self, nav_point):
        if nav_point not in self.stars:
            self.stars.append(nav_point)

    def get_position(self):
        # Se usa la posición del primer SID si existe
        if self.sids:
            return self.sids[0].get_coords()
        return None

    def __repr__(self):
        sid_names = [p.name for p in self.sids]
        star_names = [p.name for p in self.stars]
        return f"NavAirport({self.name}, SIDs={sid_names}, STARs={star_names})"