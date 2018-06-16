from django.db import models


class Profile(models.Model):
    user_id = models.ForeignKey('telegram_bot.Authentication', on_delete=models.CASCADE, default=None)
    username = models.CharField(max_length=100)
    like = models.CharField(max_length=50)
    follow = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
