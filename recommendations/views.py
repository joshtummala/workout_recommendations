from recommendations.models import Workout
from recommendations.utils import Neo4jUtils
from recommendations.serializers import UserSerializer, WorkoutSerializer

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

neo4j = Neo4jUtils()

class UserViewSet(viewsets.ViewSet):
    """ Provides create and list actions for the User model """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        """ Get all available Users """
        return Response(
            self.serializer_class(
                self.queryset,
                context={'request' : request},
                many=True).data, 
            status=status.HTTP_200_OK)

    def create(self, request):
        """ Creates a new User """
        username = request.data.get("username", None)
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        password = request.data.get("password", None)
        email = request.data.get("email", None)

        if not (username and email and password):
            return Response({
                "message": "Must include username, password and email in request"
                }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name = last_name,
            )
            user.set_password(password)
            user.save()
            neo4j.run(f"CREATE (u:User{{username:\"{user.username}\", id:{user.id}}})")

        return Response(
            self.serializer_class(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class CustomAuthToken(ObtainAuthToken):
    """ Custom Token creation view """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class WorkoutViewSet(viewsets.ViewSet):
    """ Provides create and list actions for the Workout model """

    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """ Get all available Workouts the user has done """
        return Response(
            self.serializer_class(
                self.queryset.filter(user=request.user),
                context={'request' : request},
                many=True).data, 
            status=status.HTTP_200_OK)

    def create(self, request):
        """ Creates a new Workout """
        user = request.user
        name = request.user.get("name", None)
        if not name:
            return Response({
                "message": "Must include name in request"
                }, status=status.HTTP_400_BAD_REQUEST)
        workout = Workout(name=name, user=user)
        return Response(
            self.serializer_class(workout, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def patch(self, request, workout_id):
        """ Add an Exercises to a workout """
        workout = Workout.objects.get(id=workout_id)
        if workout.user.id != request.user.id:
            return Response(
                {"message": "You do not have access to the Workout"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        add_exercises = request.data.get("add", {"exercises": []}).get("exercises", [])
        for exercise in add_exercises:
            workout.exercises.add(exercise)
        return Response(
            self.serializer_class(workout, context={'request': request}).data,
            status=status.HTTP_200_OK
        )