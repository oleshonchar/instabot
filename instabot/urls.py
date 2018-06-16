from django.contrib import admin
from django.urls import path
from telegram_bot import views
from .settings import TG_TOKEN

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bot/{}'.format(TG_TOKEN), views.CommandReceiveView.as_view(), name='webhook'),
]
