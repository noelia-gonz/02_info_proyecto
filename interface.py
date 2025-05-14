import tkinter as tk
from tkinter import filedialog, messagebox
from graph import Graph
from node import Node, Distance
from test_graph import CreateGraph_1
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, Arrow


class GraphInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Air Route Explorer - Versión Final")
        self.root.geometry("1000x800")

        # Estado de la aplicación
        self.graph = Graph()
        self.mode = "add"
        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.fixed_zoom = False
        self.zoom_limits = None

        # Configuración de colores
        self.colors = {
            'normal': '#1f77b4',
            'selected': '#ff7f0e',
            'neighbor': '#2ca02c',
            'reachable': '#d62728',
            'path': '#9467bd',
            'start': '#8c564b',
            'end': '#e377c2'
        }

        self.setup_ui()
        self.load_example()

    def setup_ui(self):
        """Configura todos los elementos de la interfaz"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de controles
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Frame de gráfico
        graph_frame = tk.Frame(main_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True)

        # Botones de control
        tk.Button(control_frame, text="Ejemplo", command=self.load_example).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Cargar", command=self.load_graph).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Guardar", command=self.save_graph).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Limpiar", command=self.clear_graph).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Bloquear Zoom", command=self.toggle_zoom).pack(side=tk.LEFT)

        # Botones de modo
        self.add_btn = tk.Button(control_frame, text="Añadir Nodos", command=lambda: self.set_mode("add"))
        self.add_btn.pack(side=tk.LEFT, padx=5)
        self.connect_btn = tk.Button(control_frame, text="Conectar Nodos", command=lambda: self.set_mode("connect"))
        self.connect_btn.pack(side=tk.LEFT)

        # Frame de búsqueda
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(search_frame, text="Nodo:").pack(side=tk.LEFT)
        self.node_entry = tk.Entry(search_frame, width=10)
        self.node_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Buscar Vecinos", command=self.find_neighbors).pack(side=tk.LEFT)

        # Frame de alcance
        reach_frame = tk.Frame(main_frame)
        reach_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(reach_frame, text="Alcance desde:").pack(side=tk.LEFT)
        self.reach_entry = tk.Entry(reach_frame, width=10)
        self.reach_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(reach_frame, text="Mostrar Alcance", command=self.show_reachable).pack(side=tk.LEFT)

        # Frame de ruta más corta
        path_frame = tk.Frame(main_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(path_frame, text="Ruta más corta:").pack(side=tk.LEFT)
        self.start_entry = tk.Entry(path_frame, width=10)
        self.start_entry.pack(side=tk.LEFT)
        tk.Label(path_frame, text="a").pack(side=tk.LEFT)
        self.end_entry = tk.Entry(path_frame, width=10)
        self.end_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="Calcular Ruta", command=self.find_shortest_path).pack(side=tk.LEFT)

        # Configurar el gráfico
        self.setup_graph(graph_frame)

        # Barra de estado
        self.status = tk.Label(main_frame, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X)

    def setup_graph(self, parent_frame):
        """Configura el área de visualización del gráfico"""
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.ax.set_title("Explorador de Rutas Aéreas")
        self.ax.grid(True)

    def toggle_zoom(self):
        """Alterna el bloqueo del zoom"""
        self.fixed_zoom = not self.fixed_zoom

        if self.fixed_zoom and self.graph.nodes:
            xs = [n.x for n in self.graph.nodes]
            ys = [n.y for n in self.graph.nodes]
            x_margin = max(3, (max(xs) - min(xs))*0.2 )
            y_margin = max(3, (max(ys) - min(ys))*0.2 )
            self.zoom_limits = (min(xs) - x_margin, max(xs) + x_margin, min(ys) - y_margin, max(ys) + y_margin)
            self.update_status("Zoom bloqueado")
        else:
            self.zoom_limits = None
            self.update_status("Zoom automático")
            self.update_drawing()

    def set_mode(self, mode):
        """Establece el modo de interacción"""
        self.mode = mode
        self.selected_node = None
        self.add_btn.config(relief=tk.SUNKEN if mode == "add" else tk.RAISED)
        self.connect_btn.config(relief=tk.SUNKEN if mode == "connect" else tk.RAISED)
        self.update_status(f"Modo: {'Añadir nodos' if mode == 'add' else 'Conectar nodos'}")
        self.update_drawing()

    def on_click(self, event):
        """Maneja clics en el área del gráfico"""
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata

        if self.mode == "add":
            name = f"N{len(self.graph.nodes) + 1}"
            self.graph.add_node(Node(name, x, y))
            self.update_status(f"Nodo {name} añadido en ({x:.1f}, {y:.1f})")
        elif self.mode == "connect":
            clicked_node = self.graph.closest(x, y)

            if clicked_node:
                if not self.selected_node:
                    self.selected_node = clicked_node
                    self.update_status(f"Seleccionado {clicked_node.name}. Elija nodo destino")
                else:
                    if self.selected_node != clicked_node:
                        if clicked_node in self.selected_node.neighbors:
                            self.update_status(f"Conexión {self.selected_node.name}→{clicked_node.name} ya existe")
                        else:
                            self.graph.connect(self.selected_node.name, clicked_node.name)
                            self.graph.connect(clicked_node.name, self.selected_node.name)
                            self.update_status(f"Conectado {self.selected_node.name} ↔ {clicked_node.name}")
                    else:
                        self.update_status("No se puede conectar un nodo consigo mismo")
                    self.selected_node = None

        self.update_drawing()

    def load_example(self):
        """Carga el gráfico de ejemplo"""
        self.graph = CreateGraph_1()
        self.update_status("Gráfico de ejemplo cargado")
        self.update_drawing()

    def load_graph(self):
        """Carga un gráfico desde archivo"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            try:
                self.graph = Graph.load_from_file(filename)
                self.update_status(f"Gráfico cargado desde {filename}")
                self.update_drawing()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")

    def save_graph(self):
        """Guarda el gráfico actual en un archivo"""
        if not self.graph.nodes:
            messagebox.showwarning("Advertencia", "No hay nodos para guardar")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            try:
                self.graph.save_to_file(filename)
                self.update_status(f"Gráfico guardado en {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def clear_graph(self):
        """Limpia el gráfico actual"""
        self.graph = Graph()
        self.selected_node = None
        self.reachable_nodes = []
        self.shortest_path = []
        self.update_status("Gráfico limpiado")
        self.update_drawing()

    def find_neighbors(self):
        """Resalta los vecinos de un nodo"""
        node_name = self.node_entry.get()
        node = self.graph.get_node_by_name(node_name)

        if node:
            self.reachable_nodes = []
            self.shortest_path = []
            self.selected_node = node
            self.update_status(f"Vecinos de {node_name}: {', '.join(n.name for n in node.neighbors)}")
        else:
            self.update_status(f"Nodo {node_name} no encontrado")
        self.update_drawing()

    def show_reachable(self):
        """Muestra todos los nodos alcanzables desde un nodo"""
        node_name = self.reach_entry.get()
        node = self.graph.get_node_by_name(node_name)

        if node:
            self.reachable_nodes = self.graph.reachable_nodes(node_name)
            self.shortest_path = []
            self.update_status(f"Nodos alcanzables desde {node_name}: {len(self.reachable_nodes)} nodos")
        else:
            self.update_status(f"Nodo {node_name} no encontrado")
        self.update_drawing()

    def find_shortest_path(self):
        """Calcula y muestra la ruta más corta entre dos nodos"""
        start_name = self.start_entry.get()
        end_name = self.end_entry.get()

        start_node = self.graph.get_node_by_name(start_name)
        end_node = self.graph.get_node_by_name(end_name)

        if not start_node or not end_node:
            self.update_status("Error: Uno o ambos nodos no existen")
            return

        path = self.graph.FindShortestPath(start_name, end_name)

        if path:
            self.shortest_path = path.nodes
            self.reachable_nodes = []
            self.update_status(f"Ruta más corta: {' → '.join(n.name for n in path.nodes)} (Costo: {path.cost:.2f})")
        else:
            self.shortest_path = []
            self.update_status(f"No hay ruta entre {start_name} y {end_name}")
        self.update_drawing()

    def update_drawing(self):
        """Actualiza el gráfico con el estado actual"""
        self.ax.clear()

        # Dibujar todos los segmentos
        for node in self.graph.nodes:
            for neighbor in node.neighbors:
                if node.name < neighbor.name:  # Dibujar solo una vez por par
                    self.draw_segment(node, neighbor)

        # Resaltar ruta más corta
        if len(self.shortest_path) > 1:
            for i in range(len(self.shortest_path) - 1):
                start = self.shortest_path[i]
                end = self.shortest_path[i + 1]
                self.draw_segment(start, end, is_path=True)

        # Dibujar todos los nodos
        for node in self.graph.nodes:
            self.draw_node(node)

        # Configuración del gráfico
        self.ax.grid(True)
        self.ax.set_xlabel("Coordenada X")
        self.ax.set_ylabel("Coordenada Y")
        self.ax.set_title("Explorador de Rutas Aéreas")

        # Aplicar límites de zoom
        if self.fixed_zoom and self.zoom_limits:
            self.ax.set_xlim(self.zoom_limits[0], self.zoom_limits[1])
            self.ax.set_ylim(self.zoom_limits[2], self.zoom_limits[3])
        elif self.graph.nodes:
            xs = [n.x for n in self.graph.nodes]
            ys = [n.y for n in self.graph.nodes]
            x_margin = max(3, (max(xs) - min(xs)) * 0.2)
            y_margin = max(3, (max(ys) - min(ys)) * 0.2)
            self.ax.set_xlim(min(xs) - x_margin, max(xs) + x_margin)
            self.ax.set_ylim(min(ys) - y_margin, max(ys) + y_margin)

        self.canvas.draw()

    def draw_segment(self, start, end, is_path=False):
        """Dibuja un segmento entre dos nodos"""
        color = self.colors['path'] if is_path else '#aaaaaa'
        linewidth = 2 if is_path else 1

        # Dibujar flecha
        arrow = Arrow(start.x, start.y, end.x - start.x, end.y - start.y,
                      width=0.2, color=color, linewidth=linewidth)
        self.ax.add_patch(arrow)

        # Mostrar costo
        mid_x = (start.x + end.x) / 2
        mid_y = (start.y + end.y) / 2
        cost = Distance(start, end)
        self.ax.text(mid_x, mid_y, f"{cost:.1f}", ha='center', va='center',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    def draw_node(self, node):
        """Dibuja un nodo con el estilo apropiado"""
        if node in self.shortest_path:
            if node == self.shortest_path[0]:
                color = self.colors['start']
            elif node == self.shortest_path[-1]:
                color = self.colors['end']
            else:
                color = self.colors['path']
        elif node == self.selected_node:
            color = self.colors['selected']
        elif node in self.reachable_nodes:
            color = self.colors['reachable']
        elif any(node in n.neighbors for n in [self.selected_node] if self.selected_node):
            color = self.colors['neighbor']
        else:
            color = self.colors['normal']

        circle = Circle((node.x, node.y), 0.4, color=color, zorder=10)
        self.ax.add_patch(circle)
        self.ax.text(node.x, node.y + 0.5, node.name, ha='center', va='center',
                     fontsize=10, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    def update_status(self, message):
        """Actualiza la barra de estado"""
        self.status.config(text=message)
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphInterface(root)
    root.mainloop()