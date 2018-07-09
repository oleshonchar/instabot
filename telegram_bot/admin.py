from django.contrib import admin
from .models import *


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TgUser._meta.fields]
