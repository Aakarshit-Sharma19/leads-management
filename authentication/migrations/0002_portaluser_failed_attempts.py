# Generated by Django 4.1.3 on 2022-11-28 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="portaluser",
            name="failed_attempts",
            field=models.IntegerField(default=0),
        ),
    ]
