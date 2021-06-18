from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class BodyPart(models.Model):
    """ Represents a human body part """
    
    name = models.CharField(max_length=100)

class Exercise(models.Model):
    """ Represents an Exercise """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    body_part = models.ManyToManyField(BodyPart)


class Workout(models.Model):
    """ Represents a Workout that contains multiple Exercises """

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    exercises = models.ManyToManyField(Exercise)
    day = models.DateField(default=now())