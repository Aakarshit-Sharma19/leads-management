# Generated by Django 4.1.3 on 2022-12-06 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0002_alter_portaluser_username"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="portaluser",
            name="username",
        ),
    ]
