from graph import Graph
from node import Node


def CreateGraph_1():
    G = Graph()



    G.add_node(Node("A", 1, 20))
    G.add_node(Node("B", 8, 17))
    G.add_node(Node("C", 15, 20))
    G.add_node(Node("D", 18, 15))
    G.add_node(Node("E", 2, 4))
    G.add_node(Node("F", 6, 5))
    G.add_node(Node("G", 12, 12))
    G.add_node(Node("H", 10, 3))
    G.add_node(Node("I", 19, 1))
    G.add_node(Node("J", 13, 5))
    G.add_node(Node("K", 3, 15))
    G.add_node(Node("L", 4, 10))


    G.connect("A", "B")
    G.connect("A", "E")
    G.connect("A", "K")
    G.connect("B", "A")
    G.connect("B", "C")
    G.connect("B", "F")
    G.connect("B", "K")
    G.connect("B", "G")
    G.connect("C", "D")
    G.connect("C", "G")
    G.connect("D", "G")
    G.connect("D", "H")
    G.connect("D", "I")
    G.connect("E", "F")
    G.connect("F", "L")
    G.connect("G", "B")
    G.connect("G", "F")
    G.connect("G", "H")
    G.connect("I", "D")
    G.connect("I", "J")
    G.connect("J", "I")
    G.connect("K", "A")
    G.connect("K", "L")
    G.connect("L", "K")
    G.connect("L", "F")

    G.save_to_file("graph_data.txt")
    return G

def CreateGraph_2():
    G=Graph()

    G.add_node(Node("P", 2, 18))
    G.add_node(Node("Q", 5, 22))
    G.add_node(Node("R", 12, 19))
    G.add_node(Node("S", 15, 10))
    G.add_node(Node("T", 8, 5))
    G.add_node(Node("U", 20, 4))

    G.connect("P", "Q")
    G.connect("Q", "R")
    G.connect("R", "S")
    G.connect("S", "T")
    G.connect("T", "U")
    G.connect("U", "P")
    G.connect("Q", "S")
    G.connect("R", "T")

    return G

print("Probando el grafo...")
G = CreateGraph_1()

n = G.closest(15, 5)
print(n.name)
n = G.closest(8, 19)
print(n.name)

def CreateGraph_FromFile():
    G=Graph()
    G.load_from_file("graph_data.txt")

    print("Probando el grafo...")
    return G

    n = G.closest(15,5)
    print(n.name)
    n = G_loaded.closest(8, 19)
    print(n.name)



