# Generated by Django 3.1.1 on 2020-12-01 23:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devine', '0006_auto_20201201_2141'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='db_notification',
            unique_together={('email', 'group_name')},
        ),
    ]
