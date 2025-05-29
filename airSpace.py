from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport
from path import Path
import os
import platform
import subprocess
import matplotlib.pyplot as plt
from segment import Segment
from navAirport import NavAirport
import random
from datetime import datetime, timedelta


class AirSpace:
    def __init__(self):
        self.nav_points = {}
        self.nav_segments = []
        self.nav_airports = {}
        self.figure = None
        self.ax = None

    def load_from_files(self, nav_file, seg_file, airport_file):
        try:
            self.nav_points = {}
            self.nav_segments = []
            self.nav_airports = {}

            if os.path.exists(nav_file):
                with open(nav_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            number = int(parts[0])
                            name = parts[1]
                            lat = float(parts[2])
                            lon = float(parts[3])
                            self.nav_points[number] = NavPoint(number, name, lat, lon)
            else:
                raise FileNotFoundError(f"Navigation points file not found: {nav_file}")

            print(f"Loaded NavPoints: {len(self.nav_points)}")

            if os.path.exists(seg_file):
                with open(seg_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            origin = int(parts[0])
                            dest = int(parts[1])
                            distance = float(parts[2])
                            segment = NavSegment(origin, dest, distance,
                                                 origin_point=self.nav_points.get(origin),
                                                 destination_point=self.nav_points.get(dest))
                            self.nav_segments.append(segment)

                            if origin in self.nav_points and dest in self.nav_points:
                                self.nav_points[origin].add_neighbor(self.nav_points[dest])
                                self.nav_points[dest].add_neighbor(self.nav_points[origin])  # Bidirectional
                            else:
                                print(f"Segment ignored: {origin} → {dest} (node not found)")
            else:
                raise FileNotFoundError(f"Segments file not found: {seg_file}")

            print(f"Valid NavSegments loaded: {len(self.nav_segments)}")

            if airport_file and os.path.exists(airport_file):
                with open(airport_file, 'r') as f:
                    current_airport = None
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        if line.isupper() and len(line) == 4:  # Airport code
                            current_airport = NavAirport(line)
                            self.nav_airports[line] = current_airport
                        elif line.endswith('.D'):  # Departure point
                            point = self.find_point_by_name(line)
                            if point and current_airport:
                                current_airport.sids.append(point)
                        elif line.endswith('.A'):  # Arrival point
                            point = self.find_point_by_name(line)
                            if point and current_airport:
                                current_airport.stars.append(point)
            else:
                print(f"⚠️ Airport file not found or not specified: {airport_file}")

            print(f"Airports loaded: {len(self.nav_airports)}")
            return True

        except Exception as e:
            print(f" Error loading files: {e}")
            raise e

    def load_from_saved_graph(self, filename):
        self.nav_points = {}
        self.nav_segments = []
        self.nav_airports = {}

        mode = None
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    if "NavPoints" in line:
                        mode = "nav"
                    elif "Segments" in line:
                        mode = "seg"
                    elif "Airports" in line:
                        mode = "air"
                    continue

                parts = line.split(',')

                if mode == "nav":
                    number = int(parts[0])
                    name = parts[1]
                    lat = float(parts[2])
                    lon = float(parts[3])
                    self.nav_points[number] = NavPoint(number, name, lat, lon)

                elif mode == "seg":
                    origin_number = int(parts[0])
                    dest_number = int(parts[1])
                    cost = float(parts[2]) if len(parts) > 2 else None

                    origin = self.nav_points.get(origin_number)
                    destination = self.nav_points.get(dest_number)
                    if origin and destination:
                        origin.add_neighbor(destination)
                        destination.add_neighbor(origin)
                        segment = NavSegment(origin_number, dest_number, cost,
                                             origin_point=origin, destination_point=destination)
                        self.nav_segments.append(segment)
                    else:
                        print(f"⚠ Segment ignored: {origin_number} → {dest_number} (node not found)")

                elif mode == "air":
                    name = parts[0]
                    lat = float(parts[1])
                    lon = float(parts[2])
                    self.nav_airports[name] = NavAirport(name)
                    dummy_point = NavPoint(-1, name, lat, lon)
                    self.nav_airports[name].sids.append(dummy_point)

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

    def add_segment(self, origin_number, destination_number):
        if origin_number in self.nav_points and destination_number in self.nav_points:
            origin = self.nav_points[origin_number]
            destination = self.nav_points[destination_number]

            segment_name = f"{origin.name}-{destination.name}"
            self.nav_segments.append(NavSegment(origin_number, destination_number,
                                                origin.distance_to(destination),
                                                origin_point=origin, destination_point=destination))

            # Esto añade los vecinos correctamente
            origin.add_neighbor(destination)
            destination.add_neighbor(origin)


    def draw(self, highlight_nodes=None, highlight_path=None):
        if not self.nav_points:
            print("No navigation points to display")
            return

        if not self.figure:
            self.figure, self.ax = plt.subplots(figsize=(12, 10))
        else:
            self.ax.clear()

        lons = [p.longitude for p in self.nav_points.values()]
        lats = [p.latitude for p in self.nav_points.values()]

        lon_margin = (max(lons) - min(lons)) * 0.05 or 0.1
        lat_margin = (max(lats) - min(lats)) * 0.05 or 0.1
        self.ax.set_xlim(min(lons) - lon_margin, max(lons) + lon_margin)
        self.ax.set_ylim(min(lats) - lat_margin, max(lats) + lat_margin)

        for segment in self.nav_segments:
            origin = self.nav_points.get(segment.origin_number)
            dest = self.nav_points.get(segment.destination_number)
            if origin and dest:
                self.ax.plot([origin.longitude, dest.longitude],
                             [origin.latitude, dest.latitude],
                             color='gray', alpha=0.5, linewidth=0.5)

        for point in self.nav_points.values():
            color = 'blue'
            size = 4

            if highlight_nodes and point in highlight_nodes:
                color = 'red'
                size = 6
            elif highlight_path and point in highlight_path:
                if point == highlight_path[0]:
                    color = 'green'  # Start point
                elif point == highlight_path[-1]:
                    color = 'purple'
                else:
                    color = 'orange'
                size = 6

            self.ax.plot(point.longitude, point.latitude, 'o',
                         color=color, markersize=size)
            self.ax.text(point.longitude, point.latitude + 0.01,
                         point.name, fontsize=6, ha='center')

        # Draw airports
        for airport in self.nav_airports.values():
            if airport.sids:
                position = airport.sids[0].get_coords()
                self.ax.plot(position[1], position[0], 's',
                             color='black', markersize=8)
                self.ax.text(position[1], position[0] + 0.02,
                             airport.name, fontsize=8, ha='center', weight='bold')

        # Draw highlighted path if provided
        if highlight_path and len(highlight_path) > 1:
            path_lons = [p.longitude for p in highlight_path]
            path_lats = [p.latitude for p in highlight_path]
            self.ax.plot(path_lons, path_lats, color='red',
                         linewidth=2, alpha=0.8)

        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.set_title("Catalonia Airspace")
        self.ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def generate_kml(self, filename, path_nodes=None):
        try:
            kml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>Flight Path</name>
        <Style id="yellowLine">
            <LineStyle>
                <color>7f00ffff</color>
                <width>4</width>
            </LineStyle>
        </Style>"""

            valid_points = []
            if path_nodes:
                for point in path_nodes:
                    if isinstance(point, str):
                        point = self.find_point_by_name(point)
                    if point and hasattr(point, "longitude") and hasattr(point, "latitude"):
                        valid_points.append(point)

            if valid_points:
                # Ruta de vuelo
                kml_content += """
        <Placemark>
            <name>Flight Path</name>
            <styleUrl>#yellowLine</styleUrl>
            <LineString>
                <coordinates>"""
                for p in valid_points:
                    kml_content += f"\n                {p.longitude},{p.latitude},0"
                kml_content += """
                </coordinates>
            </LineString>
        </Placemark>"""

                # Marcadores de los puntos
                for i, p in enumerate(valid_points):
                    kml_content += f"""
        <Placemark>
            <name>{p.name}</name>
            <description>Point {i + 1} of {len(valid_points)}</description>
            <Point>
                <coordinates>{p.longitude},{p.latitude},0</coordinates>
            </Point>
        </Placemark>"""

            else:
                kml_content += """
        <Placemark>
            <name>No valid path</name>
            <description>Empty or invalid path provided.</description>
        </Placemark>"""

            kml_content += """
    </Document>
    </kml>"""

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(kml_content)

        except Exception as e:
            print(f"Error generating KML: {e}")
            raise

    def export_surprise_kml(self, filename, num_flights=6):
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom.minidom import parseString

        def kml_elem(tag, **kwargs):
            e = Element(tag)
            for k, v in kwargs.items():
                e.set(k, v)
            return e

        def add_text(e, text):
            e.text = text
            return e

        kml = kml_elem('kml', xmlns="http://www.opengis.net/kml/2.2",
                       xmlns_gx="http://www.google.com/kml/ext/2.2")
        doc = SubElement(kml, 'Document')
        add_text(SubElement(doc, 'name'), 'Simulated Flights & Radars')

        # Radar style
        radar_style = SubElement(doc, 'Style', id="radarIcon")
        icon_style = SubElement(radar_style, 'IconStyle')
        icon = SubElement(icon_style, 'Icon')
        add_text(icon, 'http://maps.google.com/mapfiles/kml/shapes/radar.png')
        SubElement(icon_style, 'scale').text = "1.2"

        # Plane style
        plane_style = SubElement(doc, 'Style', id="flightIcon")
        icon_style2 = SubElement(plane_style, 'IconStyle')
        icon2 = SubElement(icon_style2, 'Icon')
        add_text(icon2, 'http://maps.google.com/mapfiles/kml/shapes/airports.png')
        SubElement(icon_style2, 'scale').text = "1.1"

        # Choose 6 random airport pairs
        airports = list(self.nav_airports.values())
        used = set()
        pairs = []
        while len(pairs) < num_flights:
            o, d = random.sample(airports, 2)
            if (o.name, d.name) not in used:
                path = self.find_shortest_path(o.name, d.name)
                if path:
                    used.add((o.name, d.name))
                    pairs.append((o, d, path))

        start_time = datetime.utcnow()

        # Generate Tracks for flights
        for i, (origin, dest, path) in enumerate(pairs):
            pmark = SubElement(doc, 'Placemark')
            add_text(SubElement(pmark, 'name'), f"Flight {i + 1}: {origin.name} to {dest.name}")
            SubElement(pmark, 'styleUrl').text = "#flightIcon"

            track = SubElement(pmark, '{http://www.google.com/kml/ext/2.2}Track')
            timestamp = start_time

            for node_name in path:
                node = self.nav_points[node_name]
                coord = f"{node.longitude},{node.latitude},10000"
                add_text(SubElement(track, '{http://www.google.com/kml/ext/2.2}when'), timestamp.isoformat() + "Z")
                add_text(SubElement(track, '{http://www.google.com/kml/ext/2.2}gx:coord'), coord)
                timestamp += timedelta(seconds=10)  # 10s between points

        # Add radars at 5 random points
        radar_points = random.sample(list(self.nav_points.values()), 5)
        for i, point in enumerate(radar_points):
            radar = SubElement(doc, 'Placemark')
            add_text(SubElement(radar, 'name'), f"Radar {i + 1} ({point.name})")
            SubElement(radar, 'styleUrl').text = "#radarIcon"
            point_elem = SubElement(radar, 'Point')
            add_text(SubElement(point_elem, 'coordinates'), f"{point.longitude},{point.latitude},0")

        # Final output
        with open(filename, 'w', encoding='utf-8') as f:
            pretty_xml = parseString(tostring(kml)).toprettyxml(indent="  ")
            f.write(pretty_xml)
