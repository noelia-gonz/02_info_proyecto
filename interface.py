import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from airSpace import AirSpace
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
import tempfile
import time


class AirSpaceGUI:

    def __init__(self, master):
        self.master = master
        self.master.title("Airspace Visualizer")
        self.master.geometry("1200x900")

        self.airspace = AirSpace()
        self.figure, self.ax = plt.subplots(figsize=(10, 7))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()

        # Colorines
        self.colors = {
            'normal': '#00FF00',
            'selected': '#FFFF00',
            'neighbor': '#00CED1',
            'reachable': '#FF1493',
            'path': '#FF4500',
            'start': '#1E90FF',
            'end': '#FF0000',
            'highlight': '#FFFFFF',
            'segment': '#AAAAAA',
            'airport': '#FFD700'
        }

        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.shortest_path_cost = 0.0

        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.setup_controls()
        self.update_drawing()

        self.canvas.mpl_connect('button_press_event', self.on_click)
        # NO creamos aún el simulador aquí

    def get_coords(self, navpoint):
        width = self.canvas.get_tk_widget().winfo_width()
        height = self.canvas.get_tk_widget().winfo_height()
        x = (navpoint.longitude + 180) * width / 360
        y = (90 - navpoint.latitude) * height / 180
        return x, y

    def setup_controls(self):
        control_panel = ttk.Frame(self.master)
        control_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        load_frame = ttk.LabelFrame(control_panel, text="Data Loading")
        load_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        ttk.Button(load_frame, text="Load CAT",
                   command=lambda: self.load_airspace("cat")).pack(side=tk.LEFT, padx=2)
        ttk.Button(load_frame, text="Load ESP",
                   command=lambda: self.load_airspace("esp")).pack(side=tk.LEFT, padx=2)
        ttk.Button(load_frame, text="Load EUR",
                   command=lambda: self.load_airspace("eur")).pack(side=tk.LEFT, padx=2)
        ttk.Button(load_frame, text="Custom Load...",
                   command=self.load_custom).pack(side=tk.LEFT, padx=2)
        ttk.Button(load_frame, text="Clear",
                   command=self.clear_selection).pack(side=tk.LEFT, padx=2)

        node_frame = ttk.LabelFrame(control_panel, text="Node Operations")
        node_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        ttk.Label(node_frame, text="Node:").pack(side=tk.LEFT)
        self.node_entry = ttk.Entry(node_frame, width=15)
        self.node_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(node_frame, text="Find Neighbors",
                   command=self.find_neighbors).pack(side=tk.LEFT, padx=2)

        path_frame = ttk.LabelFrame(control_panel, text="Path Finding")
        path_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        ttk.Label(path_frame, text="From:").pack(side=tk.LEFT)
        self.start_entry = ttk.Entry(path_frame, width=10)
        self.start_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(path_frame, text="To:").pack(side=tk.LEFT)
        self.end_entry = ttk.Entry(path_frame, width=10)
        self.end_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(path_frame, text="Find Path",
                   command=self.find_shortest_path).pack(side=tk.LEFT, padx=2)

        export_frame = ttk.LabelFrame(control_panel, text="Export")
        ttk.Button(export_frame, text="Save Graph", command=self.save_graph).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="Load Graph", command=self.load_saved_graph).pack(side=tk.LEFT, padx=2)
        export_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        ttk.Button(export_frame, text="Export KML",
                   command=self.export_kml).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="View in GE",
                   command=self.view_in_google_earth).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="Save Simulation KML",
                   command=self.save_simulation_kml).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="Open Simulation KML",
                   command=self.open_simulation_kml).pack(side=tk.LEFT, padx=2)

    def load_airspace(self, region):
        try:
            nav_file = f"data/{region}_nav.txt"
            seg_file = f"data/{region}_seg.txt"
            airport_file = f"data/{region}_aer.txt"

            if not all(os.path.exists(f) for f in [nav_file, seg_file]):
                raise FileNotFoundError(f"Required files not found for {region}")

            self.clear_selection()
            self.airspace.load_from_files(nav_file, seg_file, airport_file)
            self.update_drawing()
            messagebox.showinfo("Success", f"{region.upper()} data loaded successfully")
        except Exception as e:
            print("Error loading airspace:", e)
            messagebox.showerror("Error", f"Failed to load {region} data:\n{str(e)}")

    def load_custom(self):
        try:
            nav_file = filedialog.askopenfilename(
                title="Select Navigation Points File",
                filetypes=[("Text files", "*.txt")])
            if not nav_file:
                return

            seg_file = filedialog.askopenfilename(
                title="Select Segments File",
                filetypes=[("Text files", "*.txt")])
            if not seg_file:
                return

            airport_file = filedialog.askopenfilename(
                title="Select Airports File (optional)",
                filetypes=[("Text files", "*.txt")])

            self.clear_selection()
            self.airspace.load_from_files(nav_file, seg_file, airport_file)
            self.update_drawing()
            messagebox.showinfo("Success", "Custom data loaded successfully")
        except Exception as e:
            print("Error loading custom airspace:", e)
            messagebox.showerror("Error", f"Failed to load custom data:\n{str(e)}")

    def clear_selection(self):
        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.shortest_path_cost = 0.0
        self.airspace.nav_points.clear()
        self.airspace.nav_segments.clear()
        self.airspace.nav_airports.clear()
        self.update_drawing()

    #Guardar grafo con nodos, segmentos,...
    def save_graph(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save Graph As"
        )

        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                # Guardar NavPoints
                f.write("# NavPoints\n")
                for nav in self.airspace.nav_points.values():
                    f.write(f"{nav.number},{nav.name},{nav.latitude},{nav.longitude}\n")

                # Guardar Segments con coste
                f.write("# Segments\n")
                for seg in self.airspace.nav_segments:
                    if seg.origin and seg.destination:
                        f.write(f"{seg.origin.number},{seg.destination.number},{seg.cost}\n")
                    else:
                        print(f"⚠Segmento inválido (uno de los extremos es None): {seg}")

                # Guardar Airports
                f.write("# Airports\n")
                for airport in self.airspace.nav_airports.values():
                    if airport.sids:
                        lat, lon = airport.sids[0].get_coords()
                        f.write(f"{airport.name},{lat},{lon}\n")

            messagebox.showinfo("Success", f"Graph saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save graph: {str(e)}")

    #Cargar grafo
    def load_saved_graph(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Open Saved Graph"
        )

        if not filename:
            return

        try:
            self.clear_selection()
            self.airspace.load_from_saved_graph(filename)
            self.update_drawing()
            messagebox.showinfo("Success", "Saved graph loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load saved graph: {str(e)}")



    def find_neighbors(self):
        name = self.node_entry.get()
        self.selected_node = self.airspace.find_point_by_name(name)
        if not self.selected_node:
            messagebox.showwarning("Warning", f"Node '{name}' not found")
            return
        self.reachable_nodes = []
        self.shortest_path = []
        self.update_drawing()

    def show_reachable(self):
        name = self.reach_entry.get()
        self.reachable_nodes = self.airspace.reachable_nodes(name)
        if not self.reachable_nodes:
            messagebox.showwarning("Warning", f"No reachable nodes from '{name}'")
        self.selected_node = None
        self.shortest_path = []
        self.update_drawing()

    def find_shortest_path(self):
        start = self.start_entry.get()
        end = self.end_entry.get()

        path = self.airspace.find_shortest_path(start, end)
        if path:
            self.shortest_path = path.nodes
            self.shortest_path_cost = path.cost
            messagebox.showinfo("Shortest Path", f"Total cost: {path.cost:.2f} km")
        else:
            messagebox.showinfo("Shortest Path", f"No path between {start} and {end}")
            self.shortest_path = []
            self.shortest_path_cost = 0.0

        self.selected_node = None
        self.reachable_nodes = []
        self.update_drawing()

    def plan_flight(self):
        waypoints = [w.strip() for w in self.waypoint_entry.get().split(',') if w.strip()]

        if len(waypoints) < 2:
            messagebox.showwarning("Warning", "Please enter at least 2 waypoints separated by commas")
            return

        complete_route = self.airspace.plan_flight(waypoints)
        if not complete_route:
            messagebox.showinfo("Flight Plan", "No valid route found for the given waypoints")
            return

        self.shortest_path = complete_route
        self.shortest_path_cost = sum(
            complete_route[i].distance_to(complete_route[i + 1])
            for i in range(len(complete_route) - 1)
        )

        messagebox.showinfo("Flight Plan",
                            f"Flight planned! Total distance: {self.shortest_path_cost:.2f} km")
        self.update_drawing()

    def export_kml(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=[("KML Files", "*.kml"), ("All Files", "*.*")],
            initialfile="airspace_view.kml"
        )

        if not filename:
            return

        try:
            # Solo exportamos la ruta más corta
            self.airspace.generate_kml(filename, self.shortest_path)
            messagebox.showinfo("Success", f"KML file saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export KML: {str(e)}")

    def view_in_google_earth(self):
        if not self.shortest_path:
            messagebox.showwarning("No Path", "Please calculate a path first")
            return

        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            kml_file = os.path.join(temp_dir, f"flight_path_{int(time.time())}.kml")

            elements = {
                'points': True,
                'segments': True,
                'airports': True,
                'reachable': [],
                'path': self.shortest_path
            }
            self.airspace.generate_kml(kml_file, elements)
            if platform.system() == 'Windows':
                os.startfile(kml_file)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', kml_file])
            else:
                subprocess.call(['xdg-open', kml_file])

            messagebox.showinfo("Success", "Opening flight path in Google Earth...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Google Earth: {str(e)}")
    def on_click(self, event):
        if event.xdata and event.ydata:
            print(f"Clicked at: ({event.xdata:.4f}, {event.ydata:.4f})")

    def update_drawing(self):
        self.ax.clear()
        self.figure.patch.set_facecolor("black")
        self.ax.set_facecolor("black")

        if not self.airspace.nav_points:
            self.ax.set_title("No data loaded")
            self.canvas.draw()
            return

        lons = [p.longitude for p in self.airspace.nav_points.values()]
        lats = [p.latitude for p in self.airspace.nav_points.values()]

        lon_margin = (max(lons) - min(lons)) * 0.05 or 0.1
        lat_margin = (max(lats) - min(lats)) * 0.05 or 0.1

        self.ax.set_xlim(min(lons) - lon_margin, max(lons) + lon_margin)
        self.ax.set_ylim(min(lats) - lat_margin, max(lats) + lat_margin)

        # Segmentos
        for seg in self.airspace.nav_segments:
            origin = seg.origin
            dest = seg.destination
            if origin and dest:
                if (self.shortest_path and
                        origin in self.shortest_path and
                        dest in self.shortest_path and
                        abs(self.shortest_path.index(origin) - self.shortest_path.index(dest)) == 1):
                    self.ax.plot([origin.longitude, dest.longitude],
                                 [origin.latitude, dest.latitude],
                                 color=self.colors['highlight'], linewidth=2, alpha=1.0)
                else:
                    self.ax.plot([origin.longitude, dest.longitude],
                                 [origin.latitude, dest.latitude],
                                 color=self.colors['segment'], linewidth=1, alpha=0.4)

        # NavPoints
        for point in self.airspace.nav_points.values():
            color = self.colors['normal']
            size = 4

            if self.selected_node and point == self.selected_node:
                color = self.colors['selected']
                size = 6
            elif self.selected_node and point in self.selected_node.neighbors:
                color = self.colors['neighbor']
                size = 5
            elif point in self.reachable_nodes:
                color = self.colors['reachable']
                size = 6
            elif point in self.shortest_path:
                if point == self.shortest_path[0]:
                    color = self.colors['start']
                elif point == self.shortest_path[-1]:
                    color = self.colors['end']
                else:
                    color = self.colors['path']
                size = 6

            self.ax.plot(point.longitude, point.latitude, 'o',
                         color=color, markersize=size, alpha=0.8)

            # Etiquetas con desplazamiento vertical proporcional
            label_offset = 0.008 * (self.ax.get_ylim()[1] - self.ax.get_ylim()[0])
            self.ax.text(point.longitude, point.latitude + label_offset,
                         point.name, fontsize=6, ha='center', color='white', alpha=0.9)

        # Aeropuertos
        for airport in self.airspace.nav_airports.values():
            if airport.sids:
                pos = airport.sids[0].get_coords()
                self.ax.plot(pos[1], pos[0], 's',
                             color=self.colors['airport'], markersize=8)
                self.ax.text(pos[1], pos[0] + 0.01, airport.name,
                             fontsize=8, ha='center', weight='bold', color='yellow')

        if self.shortest_path_cost > 0:
            self.ax.set_title(f"Shortest Path - Cost: {self.shortest_path_cost:.2f} km")
        else:
            self.ax.set_title("Airspace Visualization")

        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()


    def generate_random_flights(self):
        if self.simulator:
            self.simulator.generate_random_flights()
            self.update_drawing()
        else:
            messagebox.showwarning("Warning", "Simulator not initialized")

    def start_radar(self):
        if self.simulator:
            self.simulator.start()
        else:
            messagebox.showwarning("Warning", "Simulator not initialized")

    def stop_radar(self):
        if self.simulator:
            self.simulator.stop()
        else:
            messagebox.showwarning("Warning", "Simulator not initialized")

    def save_simulation_kml(self):
        try:
            from kml_animator import KMLAnimator

            filename = filedialog.asksaveasfilename(
                defaultextension=".kml",
                filetypes=[("KML Files", "*.kml")],
                initialfile="simulation.kml"
            )
            if not filename:
                return

            animator = KMLAnimator(self.airspace)
            animator.generate_animated_flights_kml(filename, num_flights=6)

            # Guarda la ruta en un archivo auxiliar
            with open("last_simulation_path.txt", "w") as f:
                f.write(filename)

            messagebox.showinfo("Success", f"Simulación guardada:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al guardar simulación:\n{str(e)}")
            self.last_simulation_file = filename

    def open_simulation_kml(self):
        try:
            if not os.path.exists("last_simulation_path.txt"):
                raise FileNotFoundError("No se ha guardado ninguna simulación")

            with open("last_simulation_path.txt", "r") as f:
                filename = f.read().strip()

            if not os.path.exists(filename):
                raise FileNotFoundError("No se encuentra el archivo KML guardado")

            if platform.system() == 'Windows':
                os.startfile(filename)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', filename])
            else:
                subprocess.call(['xdg-open', filename])

            messagebox.showinfo("Success", f"Abriendo:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AirSpaceGUI(root)
    root.mainloop()
