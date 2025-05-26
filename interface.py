import tkinter as tk
from tkinter import ttk, messagebox
from airSpace import AirSpace
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class AirSpaceGUI:
    """Interfaz gráfica para explorar rutas en un grafo aéreo."""

    def __init__(self, master):
        """Inicializa la interfaz de usuario con todos los elementos gráficos."""
        self.master = master
        self.master.title("Visualizador de Espacio Aéreo")
        self.master.geometry("1200x900")

        self.airspace = AirSpace()
        self.figure, self.ax = plt.subplots(figsize=(10, 7))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect('button_press_event', self.on_click)

        self.colors = {
            'normal': '#1f77b4', 'selected': '#ff7f0e', 'neighbor': '#2ca02c',
            'reachable': '#ff0000', 'path': '#9467bd', 'start': '#8c564b',
            'end': '#e377c2', 'airport': '#17becf', 'segment': '#3399ff',
            'highlight': '#00ffff'
        }

        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.shortest_path_cost = 0.0

        self.setup_controls()

    def setup_controls(self):
        """Configura los botones e inputs de la interfaz."""
        frame = ttk.Frame(self.master)
        frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        for region in ["cat", "esp", "eur"]:
            ttk.Button(frame, text=f"Cargar {region.upper()}", command=lambda r=region: self.load_airspace(r)).pack(side=tk.LEFT)

        ttk.Button(frame, text="Limpiar", command=self.clear_selection).pack(side=tk.LEFT)

        ttk.Label(frame, text="Nodo:").pack(side=tk.LEFT)
        self.node_entry = ttk.Entry(frame, width=10)
        self.node_entry.pack(side=tk.LEFT)
        ttk.Button(frame, text="Vecinos", command=self.find_neighbors).pack(side=tk.LEFT)

        ttk.Label(frame, text="Alcance:").pack(side=tk.LEFT)
        self.reach_entry = ttk.Entry(frame, width=10)
        self.reach_entry.pack(side=tk.LEFT)
        ttk.Button(frame, text="Mostrar", command=self.show_reachable).pack(side=tk.LEFT)

        ttk.Label(frame, text="Ruta: de").pack(side=tk.LEFT)
        self.start_entry = ttk.Entry(frame, width=10)
        self.start_entry.pack(side=tk.LEFT)
        ttk.Label(frame, text="a").pack(side=tk.LEFT)
        self.end_entry = ttk.Entry(frame, width=10)
        self.end_entry.pack(side=tk.LEFT)
        ttk.Button(frame, text="Calcular", command=self.find_shortest_path).pack(side=tk.LEFT)

    def clear_selection(self):
        """Limpia completamente el grafo, eliminando todos los nodos y segmentos."""
        self.airspace = AirSpace()
        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.shortest_path_cost = 0.0
        self.update_drawing()

    def load_airspace(self, region):
        """Carga un espacio aéreo desde los archivos predefinidos de una región."""
        try:
            self.airspace = AirSpace()
            self.clear_selection()
            self.airspace.load_from_files(f"data/{region}_nav.txt", f"data/{region}_seg.txt", f"data/{region}_aer.txt")
            self.update_drawing()
            messagebox.showinfo("Carga completa", f"Datos de {region.upper()} cargados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar {region.upper()}: {e}")

    def find_neighbors(self):
        """Busca y resalta los vecinos de un nodo seleccionado."""
        name = self.node_entry.get()
        self.selected_node = self.airspace.find_point_by_name(name)
        self.reachable_nodes = []
        self.shortest_path = []
        self.shortest_path_cost = 0.0
        self.update_drawing()

    def show_reachable(self):
        """Muestra los nodos alcanzables desde un nodo origen usando BFS."""
        name = self.reach_entry.get()
        self.reachable_nodes = self.airspace.reachable_nodes(name)
        self.selected_node = None
        self.shortest_path = []
        self.shortest_path_cost = 0.0
        self.update_drawing()

    def find_shortest_path(self):
        """Calcula y dibuja el camino más corto entre dos nodos usando A*."""
        start = self.start_entry.get()
        end = self.end_entry.get()
        path = self.airspace.find_shortest_path(start, end)
        if path:
            self.shortest_path = path.nodes
            self.shortest_path_cost = path.cost
            messagebox.showinfo("Ruta más corta", f"Coste total: {path.cost:.2f}")
        else:
            messagebox.showinfo("Ruta más corta", f"No hay ruta entre {start} y {end}")
            self.shortest_path = []
            self.shortest_path_cost = 0.0
        self.selected_node = None
        self.reachable_nodes = []
        self.update_drawing()

    def on_click(self, event):
        """Muestra por consola las coordenadas del click (debug opcional)."""
        print(f"Click en ({event.xdata}, {event.ydata})")

    def update_drawing(self):
        """Redibuja el grafo con los elementos resaltados según la acción actual."""
        self.ax.clear()
        if not self.airspace.nav_points:
            self.canvas.draw()
            return

        lons = [p.longitude for p in self.airspace.nav_points.values()]
        lats = [p.latitude for p in self.airspace.nav_points.values()]

        lon_margin = (max(lons) - min(lons)) * 0.05 or 0.1
        lat_margin = (max(lats) - min(lats)) * 0.05 or 0.1
        self.ax.set_xlim(min(lons) - lon_margin, max(lons) + lon_margin)
        self.ax.set_ylim(min(lats) - lat_margin, max(lats) + lat_margin)

        for p in self.airspace.nav_points.values():
            color = self.colors['normal']
            size = 4
            if self.selected_node and p == self.selected_node:
                color = self.colors['selected']
                size = 6
            elif self.selected_node and p in self.selected_node.neighbors:
                color = self.colors['neighbor']
                size = 5
            elif p in self.reachable_nodes:
                color = self.colors['reachable']
                size = 6
            elif p in self.shortest_path:
                if p == self.shortest_path[0]: color = self.colors['start']
                elif p == self.shortest_path[-1]: color = self.colors['end']
                else: color = self.colors['path']
                size = 6

            self.ax.plot(p.longitude, p.latitude, 'o', color=color, markersize=size, alpha=0.9)
            self.ax.text(p.longitude, p.latitude + 0.01, p.name, fontsize=6, ha='center', alpha=0.6)

        for seg in self.airspace.nav_segments:
            o = self.airspace.nav_points.get(seg.origin_number)
            d = self.airspace.nav_points.get(seg.destination_number)
            if o and d:
                draw_segment = False
                color = self.colors['segment']
                lw = 1.0
                alpha = 0.2

                if not self.selected_node and not self.reachable_nodes and not self.shortest_path:
                    draw_segment = True
                    alpha = 0.4

                if self.selected_node and (
                    (o == self.selected_node and d in self.selected_node.neighbors) or
                    (d == self.selected_node and o in self.selected_node.neighbors)):
                    draw_segment = True
                    color = self.colors['highlight']
                    lw = 2.5
                    alpha = 1.0

                if (self.shortest_path and o in self.shortest_path and d in self.shortest_path and
                    abs(self.shortest_path.index(o) - self.shortest_path.index(d)) == 1):
                    draw_segment = True
                    color = self.colors['highlight']
                    lw = 2.5
                    alpha = 1.0

                if draw_segment:
                    self.ax.plot([o.longitude, d.longitude], [o.latitude, d.latitude], color=color, linewidth=lw, alpha=alpha)

        if self.shortest_path_cost > 0:
            self.ax.set_title(f"Gráfico con camino. Coste = {self.shortest_path_cost:.2f}")

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = AirSpaceGUI(root)
    root.mainloop()
