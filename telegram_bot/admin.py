from django.contrib import admin
from .models import *


class AuthenticationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Authentication._meta.fields]

    class Meta:
        model = Authentication


admin.site.register(Authentication, AuthenticationAdmin)
