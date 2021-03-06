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
import datetime
from django.db import models
from django.utils import timezone
from main.models import locataire as Locataire
from main.models import financement_location as FinancementLocation
from main.models import frais_maintenance as FraisMaintenance
from main.models import suivi_loyer as SuiviLoyer
from main.models import indice_sante as IndiceSante
from main.models import alerte as Alerte
from dateutil.relativedelta import relativedelta
from django.contrib import admin
from main.models.enums import etat_suivi


INDICE_SANTE_REF_1994 = datetime.date(1994, 2, 1)
INDICE_SANTE_REF_1983 = datetime.date(1983, 1, 1)
INDICE_SANTE_REF_1981 = datetime.date(1981, 1, 1)


class ContratLocationAdmin(admin.ModelAdmin):
    raw_id_fields = ('batiment', 'assurance', 'indice_sante_base')


class ContratLocation(models.Model):
    batiment = models.ForeignKey('Batiment')
    date_debut = models.DateField(auto_now=False,  auto_now_add=False, blank=False, null=False,
                                  verbose_name=u"Date début")
    date_fin = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
    renonciation = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)
    assurance = models.ForeignKey('Assurance', blank=True, null=True)
    loyer_base = models.DecimalField(max_digits=6, decimal_places=2, default=0, blank=False, null=False)
    charges_base = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    indice_sante_base = models.ForeignKey('IndiceSante', default=None, blank=True, null=True)

    def __str__(self):
        desc = []
        if self.batiment.description:
            desc.append(self.batiment.description)
        if self.batiment.localite:
            desc.append(str(self.batiment.localite))
        period = ""
        if self.date_debut:
            period = self.date_debut.strftime('%d-%m-%Y')
        if self.date_fin:
            period += " au " + self.date_fin.strftime('%d-%m-%Y')
        desc.append(period)
        return ",".join(map(str, desc))

    @property
    def locataires(self):
        return Locataire.find_by_contrat_location(self)

    @property
    def financement_courant(self):
        list = FinancementLocation.find_by_location(self).order_by('date_fin')
        for f in list:
            return f
        return None

    @property
    def dernier_financement(self):
        list = FinancementLocation.find_by_location(self).order_by('-date_fin')
        for f in list:
            return f
        return None

    def financements(self):
        return FinancementLocation.find_by_location(self).order_by('date_debut')

    @property
    def dernier_versement(self):
        return SuiviLoyer.find_dernier_paye(self)

    def save(self,  *args, **kwargs):
        df = (self.date_debut + relativedelta(years=1))-relativedelta(days=1)
        self.date_fin = df
        self.renonciation = (self.date_debut + relativedelta(years=1))-relativedelta(days=10)
        un_indice_sante = None
        date_deb = None
        if type(self.date_debut) is datetime.datetime:
            date_deb = self.date_debut.date()
        else:
            date_deb = self.date_debut
        if date_deb < INDICE_SANTE_REF_1981:
            pass
        else:
            if date_deb < INDICE_SANTE_REF_1983:
                pass
            else:
                one_mon_timedelta = datetime.timedelta(days=1 * 365/12)
                if date_deb < INDICE_SANTE_REF_1994:
                    date_ref = self.date_debut - one_mon_timedelta
                    un_indice_sante = IndiceSante.find_by_date(date_ref)
                else:
                    date_ref = date_deb - one_mon_timedelta
                    un_indice_sante = IndiceSante.find_by_date(date_ref)

        self.indice_sante_base = un_indice_sante

        c = super(ContratLocation, self).save(*args, **kwargs)

        b = FinancementLocation.create(self.date_debut, self.date_fin, self.loyer_base, self.indice_sante_base)
        b.contrat_location = self
        b.save()
        update_suivi_alerte(self.date_debut, self, b, self.date_debut + relativedelta(years=1), 'LOCATION')
        return c

    def save_prolongation(self, type_prolongation,  *args, **kwargs):
        df = (self.date_fin + relativedelta(years=type_prolongation))
        self.date_fin = df
        self.renonciation = (self.date_fin-relativedelta(days=10))
        c = super(ContratLocation, self).save(*args, **kwargs)

        dernier_financement = self.dernier_financement
        if dernier_financement:
            if dernier_financement.date_fin:
                date_debut_nouveau_fin = dernier_financement.date_fin + relativedelta(days=1)
                dernier_financement.date_fin = self.date_fin
                dernier_financement.save()
                update_suivi_alerte(date_debut_nouveau_fin,
                                    self,
                                    dernier_financement,
                                    self.date_fin + relativedelta(days=1),
                                    'LOCATION')
        return c

    def liste_frais(self):
        return FraisMaintenance.find_by_contrat_location(self)

    def total_frais(self):
        tot = 0
        for f in FraisMaintenance.find_by_contrat_location(self):
            if f.montant:
                tot += f.montant
        return tot

    def suivis(self):
        financements = self.financements()
        suivis_liste = []
        for f in financements:
            sui = SuiviLoyer.\
                SuiviLoyer.objects.filter(financement_location=f)
            if sui.exists():
                suivis_liste.extend(sui)
        return suivis_liste

    def suivis_anterieurs(self):
        financements = self.financements()
        return SuiviLoyer.SuiviLoyer.objects.filter(financement_location__in=financements,
                                                    date_paiement__lte=timezone.now()).order_by('-date_paiement')

    def tot_suivis_paye(self):
        financements = self.financements()
        tot = 0
        for financement in financements:
            tot += self.get_total_by_financement(financement)
        return tot

    def get_total_by_financement(self, financement):
        tot = 0
        suivi_list = SuiviLoyer. \
            SuiviLoyer.objects.filter(financement_location=financement,
                                      etat_suivi__in=(etat_suivi.PAYE, etat_suivi.SURPAYE))
        if suivi_list.exists():
            for s in suivi_list:
                tot += s.loyer_percu
        return tot

    class Meta:
        ordering = ['date_debut']


def find_by_id(id):
    return ContratLocation.objects.get(pk=id)


def find_all():
    return ContratLocation.objects.all()


def search(date_fin):
    if date_fin:
        return ContratLocation.objects.filter(date_fin__gte=date_fin)

    return ContratLocation.objects.all()


def find_by_batiment_dates(a_batiment):
    return ContratLocation.objects.filter(batiment=a_batiment,
                                          date_debut__lte=timezone.now(),
                                          date_fin__gte=timezone.now())


def find_last_by_batiment(a_batiment):
    return ContratLocation.objects.filter(batiment=a_batiment, date_fin__lte=timezone.now()).last()


def find_by_batiment(a_batiment):
    return ContratLocation.objects.filter(batiment=a_batiment)


def find_by_batiment_date_debut_gte(a_batiment, location):
    # pense que c'est pas utilisé
    ContratLocation.objects.filter(batiment=a_batiment, date_debut__gte=location.date_fin)


def find_by_batiment_date_fin_lte(a_batiment, location):
    # pense que c'est pas utilisé
    ContratLocation.objects.filter(batiment=a_batiment, date_fin__lte=location.date_debut)


def update_suivi_alerte(date_debut, location, financement_location, date_fin, type_suivi):
    date_d = date_debut
    date_f = date_debut + relativedelta(months=1)
    i = 0
    while date_f <= date_fin:
        suivi = SuiviLoyer.SuiviLoyer(etat_suivi='A_VERIFIER',
                                      date_paiement=date_d,
                                      remarque=None,
                                      loyer_percu=0,
                                      charges_percu=0)
        suivi.financement_location = financement_location
        suivi.type_suivi = type_suivi
        suivi.save()
        date_d = date_d + relativedelta(months=1)
        date_f = date_f + relativedelta(months=1)
        i = i + 1
    if date_fin:
        alert = Alerte.Alerte(description='Attention fin contrat location dans 4 mois',
                              date_alerte=location.date_fin - relativedelta(months=4),
                              etat='A_VERIFIER',
                              contrat_location=location)
        alert.save()


def find_by_batiment_location(un_batiment, une_date_debut):
    return ContratLocation.objects.filter(batiment=un_batiment,
                                          date_debut__lte=une_date_debut,
                                          date_fin__gte=une_date_debut)
