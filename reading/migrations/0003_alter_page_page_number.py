# Generated by Django 5.0.1 on 2024-06-10 12:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reading', '0002_bookfeedback_bookgenre_bookrating_bookstatus_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='page_number',
            field=models.DecimalField(decimal_places=1, max_digits=6, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(9999.9)]),
        ),
    ]
