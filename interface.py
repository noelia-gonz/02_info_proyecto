
import tkinter as tk
from tkinter import filedialog, messagebox
from graph import Graph
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Air Route Explorer - Version 3")
        self.root.geometry("1200x900")

        self.graph = Graph()
        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.display_mode = "graph"
        self.fixed_zoom = False
        self.zoom_limits = None

        self.colors = {
            'normal': '#1f77b4', 'selected': '#ff7f0e', 'neighbor': '#2ca02c',
            'reachable': '#d62728', 'path': '#9467bd', 'start': '#8c564b',
            'end': '#e377c2', 'airport': '#17becf', 'sid': '#bcbd22', 'star': '#7f7f7f'
        }

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        graph_frame = tk.Frame(main_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True)

        tk.Button(control_frame, text="Modo Grafo", command=self.set_graph_mode).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Modo Espacio Aéreo", command=self.set_airspace_mode).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Cargar Catalunya", command=lambda: self.load_airspace("cat")).pack(side=tk.LEFT)

        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(search_frame, text="Nodo:").pack(side=tk.LEFT)
        self.node_entry = tk.Entry(search_frame, width=10)
        self.node_entry.pack(side=tk.LEFT)
        tk.Button(search_frame, text="Buscar Vecinos", command=self.find_neighbors).pack(side=tk.LEFT)

        reach_frame = tk.Frame(main_frame)
        reach_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(reach_frame, text="Alcance desde:").pack(side=tk.LEFT)
        self.reach_entry = tk.Entry(reach_frame, width=10)
        self.reach_entry.pack(side=tk.LEFT)
        tk.Button(reach_frame, text="Mostrar Alcance", command=self.show_reachable).pack(side=tk.LEFT)

        path_frame = tk.Frame(main_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(path_frame, text="Ruta más corta:").pack(side=tk.LEFT)
        self.start_entry = tk.Entry(path_frame, width=10)
        self.start_entry.pack(side=tk.LEFT)
        tk.Label(path_frame, text="a").pack(side=tk.LEFT)
        self.end_entry = tk.Entry(path_frame, width=10)
        self.end_entry.pack(side=tk.LEFT)
        tk.Button(path_frame, text="Calcular Ruta", command=self.find_shortest_path).pack(side=tk.LEFT)

        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.status = tk.Label(main_frame, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X)

    def set_graph_mode(self):
        self.display_mode = "graph"
        self.update_drawing()

    def set_airspace_mode(self):
        self.display_mode = "airspace"
        self.update_drawing()

    def load_airspace(self, region):
        base = f"data/{region}_"
        try:
            self.graph.load_airspace(f"{base}nav.txt", f"{base}seg.txt", f"{base}ger.txt")
            self.display_mode = "airspace"
            self.update_status(f"{region.capitalize()} cargado")

            # PRUEBA: Ver cuántos nodos se han cargado
            print("Nodos cargados:", len(self.graph.airspace.nav_points))
            print("Ejemplo:", next(iter(self.graph.airspace.nav_points.values()), None))

            self.update_drawing()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def find_neighbors(self):
        name = self.node_entry.get()
        if self.display_mode == "airspace":
            self.selected_node = self.graph.airspace.find_point_by_name(name)
            if self.selected_node:
                self.update_status(f"Vecinos de {name}: {[n.name for n in self.selected_node.neighbors]}")
            else:
                messagebox.showinfo("Info", f"Nodo '{name}' no encontrado")
        self.update_drawing()

    def show_reachable(self):
        name = self.reach_entry.get()
        if self.display_mode == "airspace":
            self.reachable_nodes = self.graph.airspace.reachable_nodes(name)
            self.update_status(f"Alcanzables desde {name}: {[n.name for n in self.reachable_nodes]}")
        self.update_drawing()

    def find_shortest_path(self):
        origin = self.start_entry.get()
        dest = self.end_entry.get()
        self.shortest_path = []
        if self.display_mode == "airspace":
            path = self.graph.airspace.find_shortest_path(origin, dest)
            if path:
                self.shortest_path = path.nodes
                self.update_status(f"Ruta más corta: {path}")
            else:
                messagebox.showinfo("Info", f"No hay ruta entre {origin} y {dest}")
        self.update_drawing()

    def update_status(self, message):
        self.status.config(text=message)
        self.root.update()

    def update_drawing(self):
        self.ax.clear()
        if self.display_mode == "airspace" and self.graph.airspace:
            # Calcular límites automáticamente
            lons = [p.longitude for p in self.graph.airspace.nav_points.values()]
            lats = [p.latitude for p in self.graph.airspace.nav_points.values()]

            if lons and lats:  # Solo si hay datos
                # Añadir un pequeño margen (10% del rango)
                lon_margin = (max(lons) - min(lons)) * 0.1
                lat_margin = (max(lats) - min(lats)) * 0.1

                self.ax.set_xlim(min(lons) - lon_margin, max(lons) + lon_margin)
                self.ax.set_ylim(min(lats) - lat_margin, max(lats) + lat_margin)

        for p in self.graph.airspace.nav_points.values():
            color = self.colors['normal']
            if self.selected_node and p == self.selected_node:
                color = self.colors['selected']
            elif p in self.reachable_nodes:
                color = self.colors['reachable']
            elif p in self.shortest_path:
                if p == self.shortest_path[0]:
                    color = self.colors['start']
                elif p == self.shortest_path[-1]:
                    color = self.colors['end']
                else:
                    color = self.colors['path']

            # Puntos más pequeños y transparentes
            self.ax.plot(p.longitude, p.latitude, 'o',
                         color=color, markersize=4, alpha=0.7)

            # Mostrar solo algunos nombres para evitar sobreposición
            if (abs(p.longitude - min(lons)) > (max(lons) - min(lons)) / 20 or
                    abs(p.latitude - min(lats)) > (max(lats) - min(lats)) / 20):
                self.ax.text(p.longitude, p.latitude + 0.01, p.name,
                             ha='center', fontsize=6, alpha=0.8)

        for seg in self.graph.airspace.nav_segments:
            o = self.graph.airspace.nav_points.get(seg.origin_number)
            d = self.graph.airspace.nav_points.get(seg.destination_number)
            if o and d:
                # Líneas más gruesas y con color distintivo
                linewidth = 1.0
                color = '#1f77b4'  # Azul
                alpha = 0.5

                # Resaltar segmentos del camino más corto
                if (self.shortest_path and
                        o in self.shortest_path and
                        d in self.shortest_path and
                        abs(self.shortest_path.index(o) - self.shortest_path.index(d)) == 1):
                    linewidth = 2.5
                    color = self.colors['path']
                    alpha = 0.9

                self.ax.plot([o.longitude, d.longitude],
                             [o.latitude, d.latitude],
                             color=color, linewidth=linewidth, alpha=alpha)
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphInterface(root)
    root.mainloop()