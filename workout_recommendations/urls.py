"""workout_recommendations URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from recommendations.views import BodyPartViewSet, ExerciseRecommendationView, ExerciseViewSet, UserViewSet, CustomAuthToken, WorkoutViewSet
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'workouts', WorkoutViewSet)
router.register(r'exercises', ExerciseViewSet)
router.register(r'body-parts', BodyPartViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^user/api-token/$', CustomAuthToken.as_view()),
    url(r'^workout/(?P<workout_id>[0-9]+)/recommendations/$', ExerciseRecommendationView.as_view()),
    url(r'^workout/(?P<workout_id>[0-9]+)/$', WorkoutViewSet.as_view({'patch': 'patch'})),
    url(r'^', include(router.urls))
]
