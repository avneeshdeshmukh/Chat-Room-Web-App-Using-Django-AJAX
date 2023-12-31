from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.


class Room(models.Model):
    creator = models.CharField(max_length=20)
    admin = models.CharField(max_length=20, default='admin')
    roomID = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=1000, default=0)

    def __str__(self):
        return self.roomID


class RoomUser(models.Model):
    user = models.CharField(max_length=20)
    room = models.CharField(max_length=10)
    joined = models.DateTimeField(default=datetime.now(), blank=True)

    def __str__(self):
        return self.user+' '+self.room


class Message(models.Model):
    user = models.CharField(max_length=20)
    content = models.TextField(max_length=100000)
    time = models.DateTimeField(default=datetime.now, blank=True)
    room = models.CharField(max_length=10)
