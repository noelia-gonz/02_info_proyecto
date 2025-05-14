
class NavAirport:
    def __init__(self, name):
        self.name = name
        self.sids = []  # List of NavPoints for departures
        self.stars = []  # List of NavPoints for arrivals