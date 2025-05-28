from node import Node
from segment import Segment

n1 = Node('Node1', 0, 0)
n2 = Node('Node2', 8, 4)
n3 = Node('Node3', 1, 5)

cam1 = Segment('Camino1', n1, n2)
cam2 = Segment('Camino2', n2, n3)

print("Segment 1:")
print("Name: {}".format(cam1.name))
print("Origin: {} ({}, {})".format(cam1.origin.name, cam1.origin.x, cam1.origin.y))
print("Destination: {} ({}, {})".format(cam1.destination.name, cam1.destination.x, cam1.destination.y))
print("Cost: {:.2f}".format(cam1.cost))
print()

print("Segment 2:")
print("Name: {}".format(cam2.name))
print("Origin: {} ({}, {})".format(cam2.origin.name, cam2.origin.x, cam2.origin.y))
print("Destination: {} ({}, {})".format(cam2.destination.name, cam2.destination.x, cam2.destination.y))
print("Cost: {:.2f}".format(cam2.cost))
print()