# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-01-22 18:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0018_personne_titre'),
    ]

    operations = [
        migrations.AddField(
            model_name='personne',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='suiviloyer',
            name='etat_suivi',
            field=models.CharField(choices=[('A_VERIFIER', 'A vérifier'), ('IMPAYE', 'Impayé'), ('EN_RETARD', 'En retard'), ('PAYE', 'Payé'), ('SURPAYE', 'Surpayé')], default='A_VERIFIER', max_length=10),
        ),
    ]