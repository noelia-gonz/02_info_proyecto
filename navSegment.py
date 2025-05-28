
class NavSegment:
    def __init__(self, origin_number, destination_number, distance, origin_point=None, destination_point=None):
        self.origin_number = int(origin_number)
        self.destination_number = int(destination_number)
        self.distance = float(distance)

        # Guardar también los objetos NavPoint si se proporcionan (opcional)
        self.origin = origin_point
        self.destination = destination_point

    def __repr__(self):
        origin_name = self.origin.name if self.origin else str(self.origin_number)
        dest_name = self.destination.name if self.destination else str(self.destination_number)
        return f"NavSegment({origin_name} → {dest_name}, {self.distance:.2f} km)"