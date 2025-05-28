from navPoint import NavPoint

# Crear dos puntos de navegación
n1 = NavPoint(1001, "GODOX", 39.3725, 1.410833)
n2 = NavPoint(1002, "KERIP", 40.9414, 0.855833)

# Comprobar distancia entre ellos
print("Distancia entre GODOX y KERIP (km):", n1.distance_to(n2))

# Probar añadir vecinos
print("Añadiendo vecino KERIP a GODOX:", n1.add_neighbor(n2))  # True
print("Intentando añadir de nuevo:", n1.add_neighbor(n2))       # False

# Verificar que el vecino está en la lista
print("Vecinos de GODOX:", n1.neighbors)

# Probar el método get_coords
print("Coordenadas de GODOX:", n1.get_coords())