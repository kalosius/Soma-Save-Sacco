# Generated by Django 5.2.2 on 2025-06-11 20:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0003_alter_borrower_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='borrower',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.borrower'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='borrower',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.borrower'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='loan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.loan'),
        ),
        migrations.AlterField(
            model_name='report',
            name='borrower',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.borrower'),
        ),
    ]
