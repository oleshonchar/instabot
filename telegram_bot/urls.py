from django.urls import path
from .views import CommandReceiveView

urlpatterns = [
    path('bot/<bot_token>/', CommandReceiveView.as_view(), name='webhook'),
]
