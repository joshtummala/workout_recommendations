from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class BodyPart(models.Model):
    """ Represents a human body part """
    
    name = models.CharField(max_length=100, blank=True)

class Exercise(models.Model):
    """ Represents an Exercise """

    name = models.CharField(max_length=100, blank=True)
    body_parts = models.ManyToManyField(BodyPart)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

class Workout(models.Model):
    """ Represents a Workout that contains multiple Exercises """

    name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, required=True)
    exercises = models.ManyToManyField(Exercise)
    day = models.DateField(default=now, required=True)