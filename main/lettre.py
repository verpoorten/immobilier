#############################################################################
#
#    Immobilier it's an application
#    designed to manage the core business of property management, buildings,
#    rental agreement and so on.
#
#    Copyright (C) 2016-2018 Verpoorten Leïla
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
from main import models as mdl
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import *
from main.forms.forms import  LettreForm, LigneForm

from templated_docs import fill_template
from templated_docs.http import FileResponse
from django.forms import formset_factory


def lettre_create(request):
    formset = None
    if request.method == 'POST':
        form = LettreForm(request.POST or None)
        formset = LigneForm(request.POST or None)
        ArticleFormSet = formset_factory(LigneForm, extra=2)
        formset = ArticleFormSet(initial=[{'test': 'Django is now open source', },
                                          {'test': 'Django is now open source2', }])
    else:
        form = LettreForm()

    if form.is_valid():
        data = form.cleaned_data
        location = data['location']

        locataires = location.locataires
        data.update({'dateJour': timezone.now()})
        data = get_personne_detail(data, locataires, location)
        data = get_batiment_detail(location.batiment, data)
        data = get_gestionnaire_detail(data)
        data.update({'tableau': [['ligne1', 'ligne2'], ['ligne1', 'ligne2']]})



        filename = fill_template(
            'documents/lettre.odt', data,
            output_format='pdf')

        return FileResponse(filename, 'lettre.{}'.format('pdf'))
    else:
        return render(request, 'documents/lettre.html', {'form': form})


def get_personne_detail(data_param, locataires, location):
    data = data_param
    personne = None
    if locataires:
        personne = location.locataires.first().personne
        if personne:
            data.update({'titre': personne.titre})
            data.update({'nom': personne.nom})
            data.update({'prenom': personne.prenom})
    return data


def get_gestionnaire_detail(data_param):
    data = data_param
    personne_gestionnaire = mdl.personne.find_gestionnaire_default()
    data.update({'gestionnaire_nom': personne_gestionnaire.nom})
    data.update({'gestionnaire_prenom': personne_gestionnaire.prenom})
    return data


def get_batiment_detail(un_batiment, data_param):
    data = data_param
    if un_batiment:
        data.update({'adresse': un_batiment.adresse_rue})
        data.update({'localite': un_batiment.adresse_localite})
    return data


class LigneTest:

    def __init__(self):
        self.col1 = "Ferrari"
        self.col2 = "Ferrari"

    def ligne_complete(self):
        return "{0} {1}".format(self.col1, self.col2)
