import tkinter as tk
from tkinter import filedialog
from graph import Graph, Node
from test_graph import CreateGraph_1
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class interface:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.G = Graph()
        self.last_node = None
        self.fixed_size = False
        # Setup inicial del grafico
        self.default_x_limits = (0, 10)
        self.default_y_limits = (0, 10)
        self.current_x_limits = self.default_x_limits
        self.current_y_limits = self.default_y_limits

        # Setup del grafico en la interfaz
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)
#BOtones:)
        tk.Button(control_frame, text="Example", command=self.load_example).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Load", command=self.load_graph).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save", command=self.save_graph).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Fix Size", command=self.toggle_fixed_size).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear Graph", command=self.clear_graph, relief=tk.RAISED, padx=5, pady=5).pack(side=tk.LEFT)


        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=5)
        self.add_mode_btn = tk.Button(mode_frame, text="Add Nodes", command=self.set_add_mode)
        self.add_mode_btn.pack(side=tk.LEFT)
        self.connect_mode_btn = tk.Button(mode_frame, text="Connect Nodes", command=self.set_connect_mode)
        self.connect_mode_btn.pack(side=tk.LEFT, padx=5)

        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Find neighbors of:").pack(side=tk.LEFT)
        self.node_entry = tk.Entry(search_frame, width=5)
        self.node_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Find", command=self.find_neighbors).pack(side=tk.LEFT)

        self.status = tk.Label(root, text="Ready")
        self.status.pack()

        self.canvas.mpl_connect("button_press_event", self.handle_click)
        self.mode = "add"
        self.update_drawing()

#Funcion para poder hacer "resizing" en el grafico
    def toggle_fixed_size(self):
        self.fixed_size = not self.fixed_size
        if self.fixed_size:
            self.current_x_limits = self.default_x_limits
            self.current_y_limits = self.default_y_limits
            self.status.config(text="Fixed size mode ON")
        else:
            self.auto_adjust_limits()
            self.status.config(text="Auto resize mode ON")
        self.update_drawing()

    def auto_adjust_limits(self):
        if not self.G.nodes:
            return

        xs = [node.x for node in self.G.nodes]
        ys = [node.y for node in self.G.nodes]

        x_margin = max(3, (max(xs) - min(xs)) * 0.2)
        y_margin = max(3, (max(ys) - min(ys)) * 0.2)

        self.current_x_limits = (min(xs) - x_margin, max(xs) + x_margin)
        self.current_y_limits = (min(ys) - y_margin, max(ys) + y_margin)
#definicion de "añadir nodos"
    def set_add_mode(self):
        self.mode = "add"
        self.last_node = None
        self.status.config(text="Mode: Add Nodes")
        self.update_drawing()
#lo mismo para los segmentos
    def set_connect_mode(self):
        self.mode = "connect"
        self.status.config(text="Mode: Connect Nodes")
        self.update_drawing()
#ejemplo
    def load_example(self):
        self.G = CreateGraph_1()
        if not self.fixed_size:
            self.auto_adjust_limits()
        self.update_drawing()
        self.status.config(text="Example graph loaded")
#file
    def load_graph(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.G = Graph.load_from_file(filename)
            if not self.fixed_size:
                self.auto_adjust_limits()
            self.update_drawing()
            self.status.config(text=f"Loaded: {filename}")

    def save_graph(self):
        if not self.G.nodes:
            self.status.config(text="No graph to save")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            self.G.save_to_file(filename)
            self.status.config(text=f"Saved to {filename}")

    def find_neighbors(self):
        name = self.node_entry.get()
        node = self.G.get_node_by_name(name)
        if node:
            neighbors = [n.name for n in node.neighbors]
            self.status.config(text=f"Neighbors of {name}: {', '.join(neighbors)}")
            self.update_drawing(focus=name)
        else:
            self.status.config(text=f"Node {name} not found")

    def handle_click(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata

        if self.fixed_size:
            x = max(self.current_x_limits[0], min(self.current_x_limits[1], x))
            y = max(self.current_y_limits[0], min(self.current_y_limits[1], y))

        if self.mode == "add":
            name = chr(65 + len(self.G.nodes)) if len(self.G.nodes) < 26 else f"N{len(self.G.nodes)}"
            self.G.add_node(Node(name, x, y))
            self.status.config(text=f"Added node {name} at ({x:.1f}, {y:.1f})")
        else:
            clicked = self.G.closest(x, y)
            if not self.last_node:
                self.last_node = clicked
                self.status.config(text=f"Selected {clicked.name}. Click target node")
            else:
                if self.last_node != clicked:
                    self.G.connect(self.last_node.name, clicked.name)
                    self.status.config(text=f"Connected {self.last_node.name} to {clicked.name}")
                self.last_node = None

        self.update_drawing()

    def update_drawing(self, focus=None):
        self.ax.clear()

        # Dibujar flechas
        for node in self.G.nodes:
            for neighbor in node.neighbors:
                dx = neighbor.x - node.x
                dy = neighbor.y - node.y
                self.ax.arrow(
                    node.x, node.y, dx * 0.9, dy * 0.85,
                    head_width=0.3, head_length=0.4,
                    fc='red', ec='red'
                )

        # Dibujar nodos
        for node in self.G.nodes:
            color = 'green' if focus and node.name == focus else ('red' if self.last_node == node else 'blue')
            self.ax.plot(node.x, node.y, 'o', markersize=15, color=color)
            self.ax.text(node.x, node.y + 0.3, node.name, ha='center')

        # límites
        self.ax.set_xlim(self.current_x_limits)
        self.ax.set_ylim(self.current_y_limits)
        self.ax.grid(True)

        title = "Graph Visualization "
        self.ax.set_title(title)

        self.canvas.draw()

    def clear_graph(self):
        self.G = Graph()
        self.last_node = None
        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_xlim(self.current_x_limits)
        self.ax.set_ylim(self.current_y_limits)
        self.canvas.draw()
        self.status.config(text="Graph cleared")


if __name__ == "__main__":
    root = tk.Tk()
    app = interface(root)
    root.mainloop()
