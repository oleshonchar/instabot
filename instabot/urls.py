from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('telegram_bot.urls', 'telegram_bot'), namespace='tg_bot'))
]
