from django.db import models


class Authentication(models.Model):
    user_id = models.IntegerField(default=None)
    username = models.CharField(max_length=50, blank=True)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'Instagram профиль пользователя'
        verbose_name_plural = 'Instagram профили'
