# Generated by Django 4.1.2 on 2022-12-01 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='allergen',
            field=models.ManyToManyField(blank=True, to='shopping.allergen'),
        ),
    ]
