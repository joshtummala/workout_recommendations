from recommendations.models import BodyPart, Exercise, Workout
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the User model """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class BodyPartSerializer(serializers.ModelSerializer):
    """ Serializer for the BodyPart model """

    class Meta:
        model = BodyPart
        field = ['id', 'name']


class ExerciseSerializer(serializers.ModelSerializer):
    """ Serializer for the Exercise model """

    body_parts = BodyPartSerializer(many=True)

    class Meta:
        model = Exercise
        field = ['id', 'name', 'body_parts', 'rating']


class WorkoutSerializer(serializers.ModelSerializer):
    """ Serializer for the Workout model """
    user = UserSerializer()
    exercises = ExerciseSerializer(many=True)

    class Meta:
        model = Workout
        fields = ['id', 'name', 'exercises', 'user', 'day']