import random
from .models import Room

def generateID():
    while True:
        # Generate a random 4-digit integer
        room_id = random.randint(1000, 9999)

        # Check if a room with the generated ID already exists
        if not Room.objects.filter(roomID=room_id).exists():
            return room_id
