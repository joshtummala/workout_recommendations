# Generated by Django 3.2.4 on 2021-06-16 01:53

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('body_part', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('day', models.DateField(default=datetime.datetime(2021, 6, 16, 1, 53, 42, 259489, tzinfo=utc))),
                ('exercises', models.ManyToManyField(to='recommendations.Exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
