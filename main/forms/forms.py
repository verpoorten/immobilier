##############################################################################
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
from django import forms
from django.forms import ModelForm
from main.models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from main import views_utils
from main import models as mdl


READONLY_ATTR = "disabled"


def get_pays_choix():
    choices_tuple = []

    list_pays = mdl.pays.Pays.objects.all()
    # list_pays = Personne.objects.values('pays_naissance').distinct()
    # list_pays = Personne.objects.all().distinct('pays_naissance')
    # list_pays = Personne.objects.order_by('pays_naissance').values_list('pays_naissance', flat=True).distinct())
    for p in list_pays:
        choices_tuple.append((p.pays, p.pays))
    if not choices_tuple:
        choices_tuple.append(('Belgique', 'Belgique'))

    return choices_tuple


class PersonneForm(forms.Form):
    # fonctionnepays_naissance = forms.ChoiceField(choices=get_pays_choix())
    nom = forms.CharField(required=True)
    prenom = forms.CharField(required=True)
    num_identite = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    # class Meta:
        # model = personne.Personne
        # fields = ['nom', 'prenom', 'email', 'profession', 'date_naissance', 'lieu_naissance', 'pays_naissance',
        #           'num_identite', 'telephone', 'gsm', 'societe']
        # autocomplete_fields = ('prenom', 'profession', 'lieu_naissance', 'pays_naissance')

    def clean(self):
        if self.cleaned_data['num_identite'] == "":
            return None
        else:
            return self.cleaned_data['num_identite']

    def __init__(self, *args, **kwargs):
        super(PersonneForm, self).__init__(*args, ** kwargs)


class BatimentForm(ModelForm):
    class Meta:
        model = batiment.Batiment
        fields = ['description', 'rue', 'numero', 'boite', 'lieu_dit', 'localite', 'superficie',
                  'performance_energetique']

    def __init__(self, *args, **kwargs):
        super(BatimentForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BatimentForm, self).clean()
        if cleaned_data.get('superficie') and cleaned_data.get('superficie') < 0:
            self.errors['superficie'] = 'Si une superficie est encodée elle doit être > à 0'


class ProprietaireForm(forms.ModelForm):
    class Meta:
        model = proprietaire.Proprietaire
        fields = ['proprietaire', 'batiment', 'date_debut', 'date_fin']

    def __init__(self, *args, **kwargs):

        # # batiment = kwargs.pop('batiment')
        # batiment= kwargs.get('sheet_id', None)
        #
        super(ProprietaireForm, self).__init__(*args, ** kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-offset-1 col-md-2'
        self.helper.field_class = 'col-md-8'
        self.helper.add_input(Submit('submit', 'Ok'))


class FraisMaintenanceForm(forms.Form):
    date_realisation = forms.DateField(required=False, input_formats=[views_utils.DATE_SHORT_FORMAT],
                                       widget=forms.DateInput(format=views_utils.DATE_SHORT_FORMAT))
    montant = forms.DecimalField(required=True, max_digits=8, decimal_places=2, localize=True)
    description = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(FraisMaintenanceForm, self).__init__(*args, ** kwargs)

    def clean(self):
        cleaned_data = super(FraisMaintenanceForm, self).clean()
        if cleaned_data.get('montant') and cleaned_data.get('montant') < 0:
            self.errors['montant'] = 'Le montant doit être > 0'
        return cleaned_data


class ContratLocationForm(forms.Form):

    date_debut = forms.DateField(required=True, input_formats=[views_utils.DATE_SHORT_FORMAT],
                                 widget=forms.DateInput(format=views_utils.DATE_SHORT_FORMAT))
    # date_fin = forms.DateField(required=False, input_formats=['%d/%m/%Y'],
    #                            widget=forms.DateInput(format='%d/%m/%Y'))
    # renonciation = forms.DateField(required=False, input_formats=['%d/%m/%Y'],
    #                                widget=forms.DateInput(format='%d/%m/%Y'))
    loyer_base = forms.DecimalField(required=True, max_digits=8, decimal_places=2, localize=True)
    charges_base = forms.DecimalField(required=True, max_digits=8, decimal_places=2, localize=True)
    assurance = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ContratLocationForm, self).__init__(*args, ** kwargs)

    def clean(self):
        cleaned_data = super(ContratLocationForm, self).clean()
        if cleaned_data.get('date_debut') and cleaned_data.get('date_fin'):
            if cleaned_data.get('date_debut') > cleaned_data.get('date_fin'):
                self.errors['date_debut'] = 'Dates erronées'
        if cleaned_data.get('loyer_base') <= 0 and cleaned_data.get('charges_base') <= 0:
            self.errors['loyer_base'] = 'Il faut au minimun un loyer ou des charges'
        return cleaned_data

    def clean_assurance(self):
        data = self.cleaned_data['assurance']

        if data is None or data == '-':
            data = None
        return data

    def clean_date_debut(self):
        data = self.cleaned_data['date_debut']

        if data is None or data == '-':
            data = None
        return data


class HonoraireForm(ModelForm):

    class Meta:
        model = honoraire.Honoraire
        fields = ['date_paiement', 'etat']

    def __init__(self, *args, **kwargs):
        super(HonoraireForm, self).__init__(*args, ** kwargs)


class FinancementLocationForm(forms.Form):
    date_debut = forms.DateField(required=True, input_formats=[views_utils.DATE_SHORT_FORMAT],
                                 widget=forms.DateInput(format=views_utils.DATE_SHORT_FORMAT))
    date_fin = forms.DateField(required=False, input_formats=[views_utils.DATE_SHORT_FORMAT],
                               widget=forms.DateInput(format=views_utils.DATE_SHORT_FORMAT))
    loyer = forms.DecimalField(required=True, max_digits=8, decimal_places=2, localize=True)
    charges = forms.DecimalField(required=True, max_digits=8, decimal_places=2, localize=True)
    index = forms.DecimalField(required=True, max_digits=8, decimal_places=2, localize=True)

    class Meta:
        model = financement_location.FinancementLocation
        fields = ['date_debut', 'date_fin', 'loyer', 'charges', 'index']


class FileForm(forms.Form):
    file = forms.FileField()


class LigneForm(forms.Form):

    test = forms.CharField(required=False)


class LettreForm(forms.Form):
    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('docx', 'MS Word'),
        ('html', 'HTML'),
    )

    sujet = forms.CharField(required=False)
    # format = forms.ChoiceField(choices=FORMAT_CHOICES)
    fichier_modele = forms.CharField(required=False)
    location = forms.ModelChoiceField(required=True, queryset=mdl.contrat_location.find_all())
    # titre = forms.CharField()

    # def __init__(self, modele_document=None, *args, **kwargs):
    #
    #     super(LettreForm, self).__init__(*args, ** kwargs)
    #

    #
    # def __init__(self, modele_document=None, *args, **kwargs):
    #     super(LettreForm, self).__init__(*args, ** kwargs)

    #     if modele_document:
    #         # self.fields['sujet'].initial = modele_document.sujet
    #         # self.fields['format'].initial = "docx"
    #         # self.fields['fichier_modele'].initial = modele_document.fichier_modele
    #         pass

    def clean(self):
        cleaned_data = super(LettreForm, self).clean()

        return cleaned_data


class SocieteForm(ModelForm):
    class Meta:
        model = societe.Societe
        fields = ['nom', 'description', 'rue', 'numero', 'boite', 'lieu_dit', 'code_postal', 'localite', 'type']
