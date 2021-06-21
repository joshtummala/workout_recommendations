from recommendations.models import Exercise, Workout
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the User model """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ExerciseSerializer(serializers.ModelSerializer):
    """ Serializer for the Exercise model """

    class Meta:
        model = Exercise
        field = ['id', 'name', 'body_parts', 'rating']


class WorkoutSerializer(serializers.ModelSerializer):
    """ Serializer for the Workout model """

    class Meta:
        model = Workout
        fields = ['id', 'name', 'exercises', 'user', 'day']
        depth = 1