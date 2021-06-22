from django.db import models
from django.contrib.auth.models import User

from recommendations.utils import date_now

class BodyPart(models.Model):
    """ Represents a human body part """
    
    name = models.CharField(max_length=100, blank=True)

class Exercise(models.Model):
    """ Represents an Exercise """
    EXERCISE_RELATIONSHIP = "IS_DONE_WITH"
    USER_RELATIONSHIP = "HAS_DONE"

    name = models.CharField(max_length=100, blank=True)
    body_parts = models.ManyToManyField(BodyPart)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

class Workout(models.Model):
    """ Represents a Workout that contains multiple Exercises """

    name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    exercises = models.ManyToManyField(Exercise)
    day = models.DateField(default=date_now, blank=True)