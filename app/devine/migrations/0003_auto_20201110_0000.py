# Generated by Django 3.1.1 on 2020-11-10 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devine', '0002_auto_20201109_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_config',
            name='day_perc',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='db_config',
            name='night_perc',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='db_config',
            name='red_perc',
            field=models.DecimalField(decimal_places=5, default=1.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='db_config',
            name='yellow_perc',
            field=models.DecimalField(decimal_places=5, default=1.0, max_digits=10),
        ),
    ]
