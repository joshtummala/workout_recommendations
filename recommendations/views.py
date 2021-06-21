from recommendations.models import BodyPart, Exercise, Workout
from recommendations.utils import Neo4jUtils
from recommendations.serializers import BodyPartSerializer, ExerciseSerializer, UserSerializer, WorkoutSerializer

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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


class BodyPartViewSet(viewsets.ViewSet):
    """ Provides create and list actions for the BodyPart model """

    queryset = BodyPart.objects.all()
    serializer_class = BodyPartSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """ Get all available BodyParts """
        return Response(
            self.serializer_class(
                self.queryset,
                context={'request' : request},
                many=True).data, 
            status=status.HTTP_200_OK)

    def create(self, request):
        """ Creates a new Exercise """
        name = request.data.get("name", None)
        if not name:
            return Response({
                "message": "Must include name in request"
                }, status=status.HTTP_400_BAD_REQUEST)
        body_part = BodyPart.objects.create(name=name)
        return Response(
            self.serializer_class(body_part, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class ExerciseViewSet(viewsets.ViewSet):
    """ Provides create and list actions for the Exercise model """

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """ Get all available Exercises """
        return Response(
            self.serializer_class(
                self.queryset,
                context={'request' : request},
                many=True).data, 
            status=status.HTTP_200_OK)

    def create(self, request):
        """ Creates a new Exercise """
        name = request.data.get("name", None)
        body_parts = request.data.get("body_parts", [])
        rating = request.data.get("rating", 0.0)
        if not name or len(body_parts) < 1:
            return Response({
                "message": "Must include name and at least 1 body part in request"
                }, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            exercise = Exercise.objects.create(name=name, rating=rating)
            neo4j.run(f"CREATE (e:Exercise{{id: {exercise.id},name: \"{exercise.name}\", rating: {exercise.rating}}})")
        existing_body_parts = BodyPart.objects.filter(name__in=body_parts)
        non_existing_body_parts = set(body_parts).difference(set(existing_body_parts.values_list("name", flat=True)))
        for name in non_existing_body_parts:
            BodyPart.objects.create(name=name)
        exercise.body_parts.add(*BodyPart.objects.filter(name__in=body_parts))
        exercise.save()
        return Response(
            self.serializer_class(exercise, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class WorkoutViewSet(viewsets.ViewSet):
    """ Provides create, list and patch actions for the Workout model """

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
        name = request.data.get("name", None)
        if not name:
            return Response({
                "message": "Must include name in request"
                }, status=status.HTTP_400_BAD_REQUEST)
        workout = Workout.objects.create(name=name, user=user)
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

        with transaction.atomic():
            with neo4j.session() as session:
                for exercise in Exercise.objects.filter(name__in=add_exercises):
                    session.run(f"""
                    MATCH (e:Exercise)-[rel:{Exercise.EXERCISE_RELATIONSHIP}]->(:Exercise{{id: \"{exercise.id}\"}})
                    WHERE e.id IN [{','.join(workout.exercises.all().values_list('id', flat=True))}]
                    SET rel.times = rel.times + 1
                    """)
                    session.run(f"""
                    MATCH (e:Exercise)<-[rel:{Exercise.EXERCISE_RELATIONSHIP}]-(:Exercise{{id: \"{exercise.id}\"}})
                    WHERE e.id IN [{','.join(workout.exercises.all().values_list('id', flat=True))}]
                    SET rel.times = rel.times + 1
                    """)
                    session.run(f"""
                    MATCH (e1:Exercise)
                    MATCH (e2:Exercise{{id: \"{exercise.id}\"}})
                    WHERE NOT (e1)-[:{Exercise.EXERCISE_RELATIONSHIP}]-(e2)
                    CREATE (e1)-[rel:{Exercise.EXERCISE_RELATIONSHIP}{{times:1}}]->(e2)
                    CREATE (e1)<-[rel:{Exercise.EXERCISE_RELATIONSHIP}{{times:1}}]-(e2)
                    """)
                    session.run(f"""
                    MATCH (:User)-[rel:{Exercise.USER_RELATIONSHIP}]->(:Exercise{{id: \"{exercise.id}\"}})
                    SET rel.times = rel.times + 1
                    """)
                    session.run(f"""
                    MATCH (u:User)
                    MATCH (e:Exercise{{id: \"{exercise.id}\"}})
                    WHERE NOT (u)-[rel:{Exercise.USER_RELATIONSHIP}]-(e)
                    CREATE (u)-[rel:{Exercise.USER_RELATIONSHIP}{{times:1}}]->(e)
                    """)
                    workout.exercises.add(exercise)

        workout.save()
        return Response(
            self.serializer_class(workout, context={'request': request}).data,
            status=status.HTTP_200_OK
        )