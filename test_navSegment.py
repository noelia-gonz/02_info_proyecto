from navPoint import NavPoint
from navSegment import NavSegment

n1 = NavPoint(6063, "IZA.D", 38.8731546833, 1.37242975)
n2 = NavPoint(6937, "LAMPA", 38.8016666667, 1.9241666667)

# Crear segmento con objetos y calcular distancia
dist = n1.distance_to(n2)
s = NavSegment(n1.number, n2.number, dist, n1, n2)

print(s)  # Debería imprimir algo como: NavSegment(IZA.D → LAMPA, 48.56 km)