import tkinter as tk
from tkinter import filedialog, messagebox
from graph import Graph
from node import Node, Distance
from test_graph import CreateGraph_1
from airSpace import AirSpace  # New for Version 3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, Arrow


class GraphInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Air Route Explorer - Version 3")
        self.root.geometry("1200x900")  # Slightly larger for new controls

        # Application state
        self.graph = Graph()
        self.mode = "add"  # Interaction mode
        self.display_mode = "graph"  # 'graph' or 'airspace'
        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.fixed_zoom = False
        self.zoom_limits = None

        # Colors for different elements
        self.colors = {
            'normal': '#1f77b4',
            'selected': '#ff7f0e',
            'neighbor': '#2ca02c',
            'reachable': '#d62728',
            'path': '#9467bd',
            'start': '#8c564b',
            'end': '#e377c2',
            'airport': '#17becf',
            'sid': '#bcbd22',
            'star': '#7f7f7f'
        }

        self.setup_ui()
        self.load_example()

    def setup_ui(self):
        """Configure all UI elements"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Control frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Graph frame
        graph_frame = tk.Frame(main_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True)

        # Mode selection buttons
        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT, padx=5)

        tk.Button(mode_frame, text="Graph Mode", command=self.set_graph_mode,
                  bg='lightblue').pack(side=tk.LEFT)
        tk.Button(mode_frame, text="Airspace Mode", command=self.set_airspace_mode,
                  bg='lightgreen').pack(side=tk.LEFT, padx=5)

        # Basic controls
        tk.Button(control_frame, text="Ejemplo", command=self.load_example).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Cargar", command=self.load_graph).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Guardar", command=self.save_graph).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Limpiar", command=self.clear_graph).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Bloquear Zoom", command=self.toggle_zoom).pack(side=tk.LEFT)

        # Airspace controls (only visible in airspace mode)
        self.airspace_control_frame = tk.Frame(control_frame)
        self.airspace_control_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(self.airspace_control_frame, text="Cargar Catalunya",
                  command=lambda: self.load_airspace("cat")).pack(side=tk.LEFT)
        tk.Button(self.airspace_control_frame, text="Cargar España",
                  command=lambda: self.load_airspace("esp")).pack(side=tk.LEFT)
        tk.Button(self.airspace_control_frame, text="Cargar Europa",
                  command=lambda: self.load_airspace("eur")).pack(side=tk.LEFT)

        # Interaction mode buttons
        self.add_btn = tk.Button(control_frame, text="Añadir Nodos",
                                 command=lambda: self.set_mode("add"))
        self.add_btn.pack(side=tk.LEFT, padx=5)
        self.connect_btn = tk.Button(control_frame, text="Conectar Nodos",
                                     command=lambda: self.set_mode("connect"))
        self.connect_btn.pack(side=tk.LEFT)

        # Search frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(search_frame, text="Nodo:").pack(side=tk.LEFT)
        self.node_entry = tk.Entry(search_frame, width=10)
        self.node_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Buscar Vecinos", command=self.find_neighbors).pack(side=tk.LEFT)

        # Reachability frame
        reach_frame = tk.Frame(main_frame)
        reach_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(reach_frame, text="Alcance desde:").pack(side=tk.LEFT)
        self.reach_entry = tk.Entry(reach_frame, width=10)
        self.reach_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(reach_frame, text="Mostrar Alcance", command=self.show_reachable).pack(side=tk.LEFT)

        # Shortest path frame
        path_frame = tk.Frame(main_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(path_frame, text="Ruta más corta:").pack(side=tk.LEFT)
        self.start_entry = tk.Entry(path_frame, width=10)
        self.start_entry.pack(side=tk.LEFT)
        tk.Label(path_frame, text="a").pack(side=tk.LEFT)
        self.end_entry = tk.Entry(path_frame, width=10)
        self.end_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="Calcular Ruta", command=self.find_shortest_path).pack(side=tk.LEFT)

        # Setup the graph display
        self.setup_graph(graph_frame)

        # Status bar
        self.status = tk.Label(main_frame, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X)

        # Initialize UI state
        self.update_ui_state()

    def setup_graph(self, parent_frame):
        """Configure the graph display area"""
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.ax.grid(True)

    def update_ui_state(self):
        """Update UI elements based on current mode"""
        if self.display_mode == "airspace":
            self.airspace_control_frame.pack(side=tk.LEFT, padx=10)
            self.add_btn.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.DISABLED)
            self.ax.set_title("Airspace Viewer")
        else:
            self.airspace_control_frame.pack_forget()
            self.add_btn.config(state=tk.NORMAL)
            self.connect_btn.config(state=tk.NORMAL)
            self.ax.set_title("Graph Viewer")
        self.update_drawing()

    def set_graph_mode(self):
        """Switch to graph mode"""
        self.display_mode = "graph"
        self.update_ui_state()
        self.update_status("Graph mode activated")

    def set_airspace_mode(self):
        """Switch to airspace mode"""
        self.display_mode = "airspace"
        self.update_ui_state()
        self.update_status("Airspace mode activated")

    def load_airspace(self, region):
        """Load airspace data for the specified region"""
        base_path = f"data/{region}_"
        try:
            self.graph.load_airspace(
                f"{base_path}nav.txt",
                f"{base_path}seg.txt",
                f"{base_path}ger.txt")
            self.display_mode = "airspace"
            self.update_status(f"{region.capitalize()} airspace loaded")
            self.update_ui_state()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load airspace:\n{str(e)}")

    def update_drawing(self):
        """Update the graph display"""
        self.ax.clear()

        if self.display_mode == "airspace":
            self.draw_airspace()
        else:
            self.draw_graph()

        # Apply zoom limits if set
        if self.fixed_zoom and self.zoom_limits:
            self.ax.set_xlim(self.zoom_limits[0], self.zoom_limits[1])
            self.ax.set_ylim(self.zoom_limits[2], self.zoom_limits[3])
        elif self.display_mode == "graph" and self.graph.nodes:
            xs = [n.x for n in self.graph.nodes]
            ys = [n.y for n in self.graph.nodes]
            x_margin = max(3, (max(xs) - min(xs)) * 0.2)
            y_margin = max(3, (max(ys) - min(ys)) * 0.2)
            self.ax.set_xlim(min(xs) - x_margin, max(xs) + x_margin)
            self.ax.set_ylim(min(ys) - y_margin, max(ys) + y_margin)
        elif self.display_mode == "airspace" and self.graph.airspace and self.graph.airspace.nav_points:
            lons = [p.longitude for p in self.graph.airspace.nav_points.values()]
            lats = [p.latitude for p in self.graph.airspace.nav_points.values()]
            lon_margin = max(1, (max(lons) - min(lons)) * 0.2)
            lat_margin = max(1, (max(lats) - min(lats)) * 0.2)
            self.ax.set_xlim(min(lons) - lon_margin, max(lons) + lon_margin)
            self.ax.set_ylim(min(lats) - lat_margin, max(lats) + lat_margin)

            self.ax.grid(True)
            self.canvas.draw()

    def draw_airspace(self):
        """Draw airspace elements"""
        if not self.graph.airspace or not self.graph.airspace.nav_points:
            return

        # Draw all segments
        for segment in self.graph.airspace.nav_segments:
            origin = self.graph.airspace.nav_points.get(segment.origin_number)
            dest = self.graph.airspace.nav_points.get(segment.destination_number)
            if origin and dest:
                color = '#aaaaaa'
                linewidth = 0.5

                # Highlight path segments if in shortest path
                if (self.shortest_path and
                        origin in self.shortest_path and
                        dest in self.shortest_path and
                        abs(self.shortest_path.index(origin) - self.shortest_path.index(dest)) == 1):
                    color = self.colors['path']
                    linewidth = 2

                self.ax.plot([origin.longitude, dest.longitude],
                             [origin.latitude, dest.latitude],
                             color=color, linewidth=linewidth)

                # Show segment cost
                mid_lon = (origin.longitude + dest.longitude) / 2
                mid_lat = (origin.latitude + dest.latitude) / 2
                self.ax.text(mid_lon, mid_lat, f"{segment.distance:.1f}",
                             ha='center', va='center', fontsize=6,
                             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

        # Draw all navigation points
        for point in self.graph.airspace.nav_points.values():
            color = self.colors['normal']
            size = 0.2

            # Highlight based on selection
            if self.selected_node and point == self.selected_node:
                color = self.colors['selected']
                size = 0.3
            elif point in self.reachable_nodes:
                color = self.colors['reachable']
                size = 0.3
            elif self.shortest_path and point in self.shortest_path:
                if point == self.shortest_path[0]:
                    color = self.colors['start']
                elif point == self.shortest_path[-1]:
                    color = self.colors['end']
                else:
                    color = self.colors['path']
                size = 0.3

            self.ax.plot(point.longitude, point.latitude, 'o',
                         markersize=size * 100, color=color)
            self.ax.text(point.longitude, point.latitude + 0.05, point.name,
                         ha='center', va='bottom', fontsize=6)

        # Draw airports
        if self.graph.airspace.nav_airports:
            for airport in self.graph.airspace.nav_airports.values():
                if airport.sids:
                    first_sid = airport.sids[0]
                    self.ax.plot(first_sid.longitude, first_sid.latitude, 's',
                                 markersize=8, color=self.colors['airport'])
                    self.ax.text(first_sid.longitude, first_sid.latitude + 0.1, airport.name,
                                 ha='center', va='bottom', fontsize=8, weight='bold',
                                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")

    def draw_graph(self):
        """Draw simple graph elements"""
        # Draw all segments
        for node in self.graph.nodes:
            for neighbor in node.neighbors:
                if node.name < neighbor.name:  # Draw only once per pair
                    is_path = (self.shortest_path and
                               node in self.shortest_path and
                               neighbor in self.shortest_path and
                               abs(self.shortest_path.index(node) - self.shortest_path.index(neighbor)) == 1)
                    self.draw_segment(node, neighbor, is_path)

        # Draw all nodes
        for node in self.graph.nodes:
            self.draw_node(node)

        self.ax.set_xlabel("Coordinate X")
        self.ax.set_ylabel("Coordinate Y")

    # ... [Keep all the existing methods like on_click, load_example, find_neighbors,
    # show_reachable, find_shortest_path, etc. from your original interface.py]
    # These methods will automatically work with both modes because they use the graph class methods

    def update_status(self, message):
        """Update the status bar"""
        self.status.config(text=message)
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphInterface(root)
    root.mainloop()