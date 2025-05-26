from navPoint import NavPoint
from navAirport import NavAirport

# Crear puntos de navegación
p1 = NavPoint(6063, "IZA.D", 38.8731, 1.3724)
p2 = NavPoint(6062, "IZA.A", 38.8772, 1.3693)

# Crear aeropuerto y añadir SIDs y STARs
a = NavAirport("LEIB")
a.add_sid(p1)
a.add_star(p2)

# Mostrar resultados
print(a)
print("Posición del aeropuerto (coords primer SID):", a.get_position())