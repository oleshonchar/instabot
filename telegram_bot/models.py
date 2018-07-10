from django.db import models


class TgUser(models.Model):
    user_id = models.IntegerField(default=None)
    username = models.CharField(max_length=50, blank=True)
    login = models.CharField(max_length=50)
    hash = models.BinaryField()
    salt = models.CharField(max_length=50)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = 'Instagram профиль пользователя'
        verbose_name_plural = 'Instagram профили'
