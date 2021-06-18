from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Exercise(models.Model):

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=100)


class Workout(models.Model):

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    exercises = models.ManyToManyField(Exercise)
    day = models.DateField(default=now())