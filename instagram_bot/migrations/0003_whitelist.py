# Generated by Django 2.0.6 on 2018-07-02 07:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0001_initial'),
        ('instagram_bot', '0002_auto_20180615_1526'),
    ]

    operations = [
        migrations.CreateModel(
            name='Whitelist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('user_id', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.Authentication')),
            ],
            options={
                'verbose_name_plural': 'Белый список',
                'verbose_name': 'Белый список',
            },
        ),
    ]