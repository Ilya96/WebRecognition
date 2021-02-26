from recognition.views import *
from django.urls import path

urlpatterns = [
    path('', recognition, name='recognition'),
]
