from django.db import models


class Profile(models.Model):
    tg_user = models.ForeignKey('telegram_bot.TgUser', on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    like = models.NullBooleanField()
    follow = models.NullBooleanField()
    unfollow = models.NullBooleanField()
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Whitelist(models.Model):
    tg_user = models.ForeignKey('telegram_bot.TgUser', on_delete=models.CASCADE)
    username = models.CharField(max_length=100)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = 'Белый список'
        verbose_name_plural = 'Белый список'
