import random
import os
import time
import platform
import tempfile

class KMLAnimator:
    def __init__(self, airspace):
        self.airspace = airspace

    def generate_animated_flights_kml(self, filename=None, num_flights=6):
        if filename is None:
            filename = os.path.join(tempfile.gettempdir(), f"simulation_{int(time.time())}.kml")

        flights = []
        airports = list(self.airspace.nav_airports.values())

        if len(airports) < 2:
            print("Not enough airports to generate flights")
            return

        for _ in range(num_flights):
            origin = random.choice(airports)
            destination = random.choice(airports)
            while destination == origin:
                destination = random.choice(airports)

            if origin.name in self.airspace.nav_points and destination.name in self.airspace.nav_points:
                path_obj = self.airspace.find_shortest_path(origin.name, destination.name)
                if path_obj and path_obj.nodes:
                    flights.append(list(path_obj.nodes))  # ⚠️ COPIA SEGURA

        # Si por algún motivo no se generó ningún vuelo
        if not flights:
            print("⚠ No valid paths generated.")
            return

        with open(filename, "w", encoding="utf-8") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
  <name>Animated Flights</name>
""")

            f.write("""
<Style id="flightStyle">
  <IconStyle>
    <scale>1.2</scale>
    <Icon>
      <href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href>
    </Icon>
  </IconStyle>
</Style>
""")

            timestamp = int(time.time())
            for i, path in enumerate(flights):
                f.write(f"<Placemark><name>Flight {i+1}</name><styleUrl>#flightStyle</styleUrl><gx:Track>")
                for j, node in enumerate(path):
                    ts = timestamp + i * 10 + j * 5
                    f.write(f"<when>{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts))}</when>")
                for node in path:
                    f.write(f"<gx:coord>{node.longitude} {node.latitude} 10000</gx:coord>")
                f.write("</gx:Track></Placemark>")

            f.write("</Document></kml>")

        print(f"KML file created: {filename}")
        #self._open_in_google_earth(filename)

    def _open_in_google_earth(self, filename):
        try:
            if platform.system() == 'Windows':
                os.startfile(filename)
            elif platform.system() == 'Darwin':
                os.system(f"open '{filename}'")
            else:
                os.system(f"xdg-open '{filename}'")
        except Exception as e:
            print(f" Error opening Google Earth: {e}")
