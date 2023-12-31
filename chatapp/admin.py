from django.contrib import admin
from chatapp.models import Room, Message, RoomUser
# Register your models here.

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(RoomUser)