# Generated by Django 5.2.2 on 2025-06-12 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients_portal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='next_of_kin',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
