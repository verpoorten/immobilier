##############################################################################
#
#    Immobilier it's an application
#    designed to manage the core business of property management, buildings,
#    rental agreement and so on.
#
#    Copyright (C) 2016-2017 Verpoorten Leïla
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db import models
from django.contrib import admin

class SocieteAdmin(admin.ModelAdmin):
    search_fields = ['nom']
    list_filter = ('localite',)


class Societe(models.Model):
    TYPE_SOCIETE = (
        ('NON_PRECISE', '-'),
        ('ASSURANCE', 'Assurance'),
        ('BANQUE', 'Banque'),
        ('NOTAIRE', 'Notaire'),
    )
    nom = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    rue = models.CharField(max_length=200, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    boite = models.CharField(max_length=10, blank=True, null=True)
    lieu_dit = models.CharField(max_length=200, blank=True, null=True)
    code_postal = models.CharField(max_length=10, blank=True, null=True)
    localite = models.ForeignKey('Localite', blank=True, null=True)
    # personnel = models.ForeignKey(Personne, blank=True, null=True)
    type = models.ForeignKey('TypeSociete', blank=True, null=True)

    @property
    def professionnels(self):
        l = Professionnel.objects.filter(societe=self)
        for ll in l:
            print(ll)
        return l



    def personnel(self):
        return Professionnel.find_by_societe(self)

    def __str__(self):
        ch = self.nom
        if self.localite:
            ch = ch + ", " + self.localite.localite
        return ch


def find_all():
    return Societe.objects.all().order_by('nom')


def find_by_id(id):
    return Societe.objects.get(pk=id)