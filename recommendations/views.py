from recommendations.serializers import UserSerializer

from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status
from rest_framework.response import Response

class UserViewSet(viewsets.ViewSet):
    """ Provides create and list actions for the User model """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        """ Get all available Users """
        return Response(
            UserSerializer(
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

        user = User.objects.create(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name = last_name,
        )
        # TODO: Add User to neo4j
        return Response({
            "message": f"User {user.id} created",
        }, status=status.HTTP_201_CREATED)


class CustomAuthToken(ObtainAuthToken):
    """ Custom Token creation view """

    def post(self, request, *args, **kwargs):
        """ Creates a new token for the given User or gets it if it exists """
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