# -*- coding: utf-8 -*-
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
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models import Sum
import datetime
import calendar


class Localite(models.Model):
    code_postal = models.CharField(max_length=10, blank=False, null=False)
    localite = models.CharField(max_length=150, blank=False, null=False)

    @staticmethod
    def find_all():
        return Localite.objects.all()

    @staticmethod
    def find_by_id(an_id):
        return Localite.objects.get(pk=an_id)

    @staticmethod
    def search(un_code_postal, une_localite):
        out = None
        queryset = Localite.objects
        if un_code_postal:
            queryset = queryset.filter(code_postal=un_code_postal)
        if une_localite:
            queryset = queryset.filter(localite__iexact=une_localite)

        if un_code_postal or une_localite:
            out = queryset
        return out

    def __str__(self):
        return self.code_postal + " " + self.localite

    class Meta:
        ordering = ['localite']


class Assurance(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    @staticmethod
    def find_all():
        return Assurance.objects.all()

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


class Banque(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


@staticmethod
def get_pays_choix():
    choices_tuple = []
    choices_tuple.append('Belgique')
    return choices_tuple


class Fonction(models.Model):
    nom_fonction = models.CharField(max_length=100, blank=False, null=False)

    @staticmethod
    def find_all():
        return Fonction.objects.all().order_by('nom_fonction')

    @staticmethod
    def find_by_nom(nom):
        l = Fonction.objects.filter(nom_fonction__iexact=nom)
        if l.exists():
            return l[0]
        return None

    def __str__(self):
        return str(self.nom_fonction)


class TypeSociete(models.Model):
    type = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.type


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
    localite = models.ForeignKey(Localite, blank=True, null=True)
    # personnel = models.ForeignKey(Personne, blank=True, null=True)
    type = models.ForeignKey(TypeSociete, blank=True, null=True)

    @property
    def professionnels(self):
        l = Professionnel.objects.filter(societe=self)
        for ll in l:
            print(ll)
        return l

    @staticmethod
    def find_all():
        return Societe.objects.all().order_by('nom')

    @staticmethod
    def find_by_id(id):
        return Societe.objects.get(pk=id)

    def personnel(self):
        return Professionnel.find_by_societe(self)

    def __str__(self):
        ch = self.nom
        if self.localite:
            ch = ch + ", " + self.localite.localite
        return ch


class Personne(models.Model):

    TYPE_PERSONNE = (
        ('NON_PRECISE', '-'),
        ('LOCATAIRE', 'Locataire'),
        ('PROFESSIONNEL', 'Professionnel'),
        ('PROPRIETAIRE', 'Propriétaire'),
        ('ANCIEN_LOCATAIRE', 'Ancien locataire'),
        ('ANCIEN_PROPRIETAIRE', 'Ancien propriétaire'),
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    # societe        = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    date_naissance = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    lieu_naissance = models.CharField(max_length=100, blank=True, null=True)
    pays_naissance = models.CharField(max_length=100, blank=True, null=True)
    num_identite = models.CharField(max_length=100, blank=True, null=True, unique=False)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    gsm = models.CharField(max_length=30, blank=True, null=True)
    societe = models.ForeignKey(Societe, blank=True, null=True)
    num_compte_banque = models.CharField(max_length=30, blank=True, null=True)
    personne_type = models.CharField(max_length=20, choices=TYPE_PERSONNE, default='NON_PRECISE', blank=True, null=True)

    def __init__(self,  *args, **kwargs):
        super(Personne, self).__init__(*args, **kwargs)
        # self._meta.get_field_by_name('pays_naissance')[0]._choices = get_pays_choix()

    def __str__(self):
        return self.nom.upper() + ", " + self.prenom

    def choix(self):
        return []
    
    @staticmethod
    def find_personne(id):
        return Personne.objects.get(pk=id)

    @property
    def batiments(self):
        proprietaire_list = Proprietaire.objects.filter(proprietaire=self)
        batiments = []
        for p in proprietaire_list:
            # batiments.append(p.batiments)
            for b in p.batiments:
                batiments.append(b)
        return batiments

    @property
    def type(self):
        type_personne = ""
        cpt = 0
        proprietaire_list = Proprietaire.objects.filter(proprietaire=self)
        if proprietaire_list.exists():
            type_personne = "proriétaire"
            cpt = cpt + 1
        locataire_list = Locataire.objects.filter(personne=self)
        if locataire_list.exists():
            if cpt > 0:
                type_personne = type_personne + ", "
            type_personne = type_personne + "locataire"
            cpt = cpt + 1
        liste = Professionnel.objects.filter(personne=self)
        if liste.exists():
            if cpt > 0:
                type_personne = type_personne + ", "
            type_personne = type_personne + "professionnel"

        return type_personne

    def contrat_gestions(self):
        proprietaire_list = Proprietaire.objects.filter(proprietaire=self)
        contrats = []
        for p in proprietaire_list:

            for b in p.batiments:
                contrat_gestion = ContratGestion.objects.filter(batiment=b)
                if contrat_gestion is not None:
                    contrats.append(contrat_gestion)
        return contrats

    @staticmethod
    def find_all():
        return Personne.objects.all()

    @staticmethod
    def find_gestionnaire_default():
        nom = 'Marchal'
        prenom = 'Stéphan'
        list_personne = Personne.objects.filter(nom=nom, prenom=prenom)
        if list_personne:
            return list_personne[0]
        return None

    class Meta:
        ordering = ['nom', 'prenom']
        unique_together = (("nom", "prenom"),)

    def save(self,  *args, **kwargs):
        p = super(Personne, self).save(*args, **kwargs)
        if Pays.objects.filter(pays=self.pays_naissance):
            pass
        else:
            if self.pays_naissance:
                pays = Pays(pays=self.pays_naissance)
                pays.save()
        fonction = None
        if self.profession:
            fonction = Fonction.find_by_nom(self.profession)
            if fonction is None:
                fonction = Fonction()
                fonction.nom_fonction = self.profession
                fonction.save()

        professionnels = Professionnel.search(self, self.societe, fonction)
        if not professionnels.exists():
            professionnel = Professionnel()
            professionnel.personne = self
            professionnel.societe = self.societe
            professionnel.fonction = fonction
            professionnel.save()

        return p


class Batiment(models.Model):
    description = models.TextField(blank=True, null=True)
    rue = models.CharField(max_length=200, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    boite = models.CharField(max_length=10, blank=True, null=True)
    lieu_dit = models.CharField(max_length=200, blank=True, null=True)
    localite = models.ForeignKey(Localite)
    superficie = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    performance_energetique = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ['localite', 'rue']

    @staticmethod
    def find_all():
        return Batiment.objects.all()

    @staticmethod
    def find_batiment(id):
        return Batiment.objects.get(pk=id)

    @staticmethod
    def find_my_batiments():
        personne = Personne.find_gestionnaire_default()
        if personne:
            return Proprietaire.find_batiment_by_personne(personne)
        return None

    @staticmethod
    def search(proprietaire=None):
        if proprietaire and proprietaire != "":
            proprio = Proprietaire.find_proprietaire(proprietaire)
            return Proprietaire.find_batiment_by_personne(proprio.proprietaire)
        return Batiment.objects.all()

    def __str__(self):
        desc = ""
        cptr = 0
        if not(self.rue is None):
            desc += " " + self.rue
            cptr = cptr + 1
        if not(self.numero is None):
            if cptr > 0:
                desc += ", "
            desc += str(self.numero)
            cptr = cptr + 1
        if not(self.boite is None):
            if cptr > 0:
                desc += ", "
            desc += self.boite
            cptr = cptr + 1
        if self.localite is not None:
            if cptr > 0:
                desc += ", "
            desc += str(self.localite.localite)
        return desc

    def adresse_rue(self):
        adresse_complete = ""
        if self.rue is not None:
            adresse_complete += self.rue
        if self.numero is not None:
            adresse_complete += " " + str(self.numero)
        if self.boite is not None:
            adresse_complete += " " + str(self.boite)
        return adresse_complete

    def adresse_localite(self):
        adresse_complete = ""
        if self.localite is not None:
            adresse_complete += " " + str(self.localite.localite)
        return adresse_complete

    def proprietaires(self):
        return Proprietaire.objects.filter(batiment=self)

    def contrats_location(self):
        return ContratLocation.objects.filter(batiment=self)

    def contrats_location_next(self):
        return ContratLocation.objects.filter(batiment=self, date_debut__gte=self.location_actuelle.date_fin)

    def contrats_location_previous(self):
        return ContratLocation.objects.filter(batiment=self, date_fin__lte=self.location_actuelle.date_debut)

    def contrat_location_next(self):
        list_c = ContratLocation.objects.filter(batiment=self, date_debut__gte=self.location_actuelle.date_fin)
        if list_c:
            return list_c[0]
        return None

    def contrat_location_previous(self):
        list_c = ContratLocation.objects.filter(batiment=self, date_fin__lte=self.location_actuelle.date_debut)
        if list_c:
            return list_c[0]
        return None

    def locataires_actuels(self):
        liste = []
        contrats = ContratLocation.objects.filter(batiment=self, 
                                                  date_debut__lte=timezone.now(), 
                                                  date_fin__gte=timezone.now())
        if not(contrats is None):
            for contrat in contrats:
                locataire = Locataire.objects.filter(contrat_location=contrat)
                for l in locataire:
                    p = Personne.find_personne(l.personne.id)
                    liste.append(p)

        return liste

    def locataires_actuels2(self):
        liste = []
        contrats = ContratLocation.objects.filter(batiment=self,
                                                  date_debut__lte=timezone.now(),
                                                  date_fin__gte=timezone.now())
        if not(contrats is None):
            for contrat in contrats:
                locataire = Locataire.objects.filter(contrat_location=contrat)
                for l in locataire:
                    if l not in liste:
                        liste.append(l)

        return liste

    def dernier_locataires(self):
        liste = []
        contrats = ContratLocation.objects.filter(batiment=self).order_by('date_fin')
        if contrats.exists():
            locataire = Locataire.objects.filter(contrat_location=contrats.last())
            for l in locataire:
                if l not in liste:
                    liste.append(l)

        return liste

    @property
    def location_actuelle(self):
        l = ContratLocation.objects.filter(batiment=self, 
                                           date_debut__lte=timezone.now(), 
                                           date_fin__gte=timezone.now()).first()
        if l:
            return l
        else:
            return ContratLocation.objects.filter(batiment=self, date_fin__lte=timezone.now()).last()

    def location_actuelle_pk(self):
        contrat_location = ContratLocation.objects.filter(batiment=self, 
                                                          date_debut__lte=timezone.now(), 
                                                          date_fin__gte=timezone.now()).first()
        if contrat_location:
            return contrat_location.id
        return None

    @property
    def contrats_gestion(self):
        return ContratGestion.objects.filter(batiment=self)

    @property
    def frais_list(self):
        return FraisMaintenance.objects.filter(batiment=self)

    @property
    def gains(self):
        tot = 0
        for c in self.contrats_location():
            for f in c.financements():
                queryset = SuiviLoyer.find_suivis_paye(f)
                aggregation = queryset.aggregate(loyer=Sum('loyer_percu'))
                loyer = aggregation.get('loyer', 0)
                tot = tot + loyer

        return tot

    @property
    def depenses(self):
        queryset = FraisMaintenance.objects.filter(batiment=self)
        aggregation = queryset.aggregate(price=Sum('montant'))
        res = aggregation.get('price', 0)

        if res:
            return res

        return 0


class Proprietaire(models.Model):
    proprietaire = models.ForeignKey(Personne, verbose_name=u"Propriétaire")
    batiment = models.ForeignKey(Batiment)
    date_debut = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False, verbose_name=u"Date début")
    date_fin = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)

    @staticmethod
    def find_proprietaire(id):
        return Proprietaire.objects.get(pk=id)

    @staticmethod
    def find_batiment_by_personne(personne):
        list_p = Proprietaire.objects.filter(proprietaire=personne)
        batiments = []
        for p in list_p:
            if p.batiment:
                batiments.append(p.batiment)
        return batiments

    @property
    def batiments(self):
        return Batiment.objects.filter(proprietaire=self)

    @staticmethod
    def find_all():
        return Proprietaire.objects.all().order_by('proprietaire')

    @staticmethod
    def find_distinct_proprietaires():
        results = Proprietaire.objects.all().order_by('proprietaire')
        liste = []
        liste_personne = []
        for result in results:
            if result.proprietaire not in liste_personne:
                liste.append(result)
                liste_personne.append(result.proprietaire)
        return liste

    def __str__(self):
        ch = ""
        ch = ch + self.proprietaire.nom
        ch = ch + self.proprietaire.prenom
        ch = ch + self.batiment.rue
        ch = ch + self.batiment.localite.localite
        return ch

    def get_absolute_url(self):
        return reverse('proprietaire_list')

    class Meta:
        unique_together = (("proprietaire", "batiment"),)


class ContratLocation(models.Model):
    batiment = models.ForeignKey(Batiment)
    date_debut = models.DateField(auto_now=False,  auto_now_add=False, blank=False, null=False,
                                  verbose_name=u"Date début")
    date_fin = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
    renonciation = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)
    assurance = models.ForeignKey('Assurance', blank=True, null=True)
    loyer_base = models.DecimalField(max_digits=6, decimal_places=2, default=0, blank=False, null=False)
    charges_base = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    # index_base  = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        desc = ""
        if not(self.batiment.description is None):
            desc += self.batiment.description
        if not(self.batiment.localite is None):
            desc += str(self.batiment.localite)
        if not(self.date_debut is None):
            desc += self.date_debut.strftime('%d-%m-%Y')
        if not(self.date_fin is None):
            desc += " au " + self.date_fin.strftime('%d-%m-%Y')
        return desc

    @property
    def locataires(self):
        return Locataire.objects.filter(contrat_location=self)

    @property
    def financement_courant(self):
        list = FinancementLocation.objects.filter(contrat_location=self)\
                                           .order_by('date_fin')
        for f in list:
            return f
        return None

    def financements(self):
        return FinancementLocation.objects.filter(contrat_location=self)

    def save_new(self,  *args, **kwargs):
        df = (self.date_debut + relativedelta(years=1))-relativedelta(days=1)
        self.date_fin = df
        self.renonciation = (self.date_debut + relativedelta(years=1))-relativedelta(days=10)

        c = super(ContratLocation, self).save(*args, **kwargs)

        b = FinancementLocation(date_debut=self.date_debut, date_fin=self.date_fin, loyer=self.loyer_base)
        b.contrat_location = self
        b.save()
        update_suivi_alerte(self.date_debut, self, b, self.date_debut + relativedelta(years=1), 'LOCATION')
        return c

    def save_prolongation(self, type_prolongation,  *args, **kwargs):
        df = (self.date_fin + relativedelta(years=type_prolongation))
        self.date_fin = df
        self.renonciation = (self.date_fin-relativedelta(days=10))
        print(self.date_fin)
        c = super(ContratLocation, self).save(*args, **kwargs)

        dernier_financement = self.financement_courant
        if dernier_financement:
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
        return FraisMaintenance.objects.filter(contrat_location=self)

    @staticmethod
    def find_all():
        return ContratLocation.objects.all()

    def suivis(self):
        financements = self.financements()
        suivis_liste = []
        for f in financements:

            sui = SuiviLoyer.objects.filter(financement_location=f)
            if sui.exists():
                suivis_liste.extend(sui)
        return suivis_liste

    @staticmethod
    def search(date_fin):
        out = None
        queryset = ContratLocation.objects
        if date_fin:
            queryset = queryset.filter(date_fin__gte=date_fin)
        if date_fin:
            out = queryset
        return out

    class Meta:
        ordering = ['date_debut']


class FinancementLocation(models.Model):
    contrat_location = models.ForeignKey(ContratLocation, default=None)
    date_debut = models.DateField(auto_now=False, auto_now_add=False, verbose_name=u"Date début")
    date_fin = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    loyer = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    charges = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    index = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        chaine = str(self.loyer) + "/" + str(self.charges)
        if self.date_debut:
            chaine = chaine + " (" + self.date_debut.strftime('%d-%m-%Y')
        if self.date_fin:
            chaine = chaine + " au " + self.date_fin.strftime('%d-%m-%Y') + ")"
        if chaine:
            return chaine
        return ""


class Professionnel(models.Model):
    personne = models.ForeignKey(Personne, blank=True, null=True)
    societe = models.ForeignKey(Societe, blank=True, null=True)
    fonction = models.ForeignKey(Fonction, blank=True, null=True)

    @staticmethod
    def find_all():
        return Professionnel.objects.all().order_by('societe')

    @staticmethod
    def search(personne=None, societe=None, fonction=None):
        out = None
        queryset = Professionnel.objects
        if personne:
            queryset = queryset.filter(personne=personne)
        if societe:
            queryset = queryset.filter(societe=societe)
        if fonction:
            queryset = queryset.filter(fonction=fonction)
        if personne or societe or fonction:
            out = queryset
        return out

    @staticmethod
    def find_by_societe(une_societe):
        return Professionnel.search(None, une_societe, None)

    def __str__(self):
        ch = ""
        if self.societe:
            ch = ch + " " + str(self.societe)
        else:
            ch = ch + " "

        if self.personne:
            ch = ch + "-" + str(self.personne)
        else:
            ch = " "

        if self.fonction:
            ch = ch + "-" + str(self.fonction)
        else:
            ch = ch + " "
        return ch


class Locataire(models.Model):
    CIVILITE = (
        ('NON_PRECISE', '-'),
        ('MADAME', 'Madame'),
        ('MADEMOISELLE', 'Mademoiselle'),
        ('MONSIEUR', 'Monsieur'),
        ('MAITRE', 'Maitre'),
        ('DOCTEUR', 'Docteur'),
    )
    personne = models.ForeignKey(Personne, error_messages={'unique': 'Please enter your name'})
    contrat_location = models.ForeignKey(ContratLocation, default=None)
    infos_complement = models.TextField(blank=True, null=True)
    principal = models.BooleanField(default=True)
    societe = models.ForeignKey(Societe, blank=True, null=True)
    tva = models.CharField(max_length=30, blank=True, null=True)
    profession = models.ForeignKey(Fonction, blank=True, null=True)
    civilite = models.CharField(max_length=15, choices=CIVILITE, default='NON_PRECISE')
    # personne_garante     = models.ForeignKey('Personne', blank=True, null=True)

    def __str__(self):
        return self.personne.nom + ", " + self.personne.prenom

    # def unique_error_message(self, model_class, unique_check):
    #     print('uni')
    #     if model_class == type(self) and unique_check == ('personne', 'contrat_location'):
    #         return "kkk"
    #     else:
    #         return super(Locataire, self).unique_error_message(model_class, unique_check)
    #
    class Meta:
        unique_together = (("personne", "contrat_location"),)

    def save(self,  *args, **kwargs):

        c = super(Locataire, self).save(*args, **kwargs)
        professionnels = Professionnel.search(self.personne, self.societe, self.profession)
        if not professionnels.exists():
            professionnel = Professionnel()
            professionnel.personne = self.personne
            professionnel.societe = self.societe
            professionnel.fonction = self.profession
            professionnel.save()
        return c

    @staticmethod
    def find_my_locataires():
        personne = Personne.find_gestionnaire_default()
        l = []
        if personne:
            batiments = Proprietaire.find_batiment_by_personne(personne)
            for b in batiments:
                l.extend(b.locataires_actuels2())
        return l


class FraisMaintenance(models.Model):
    batiment = models.ForeignKey(Batiment, verbose_name=u"Batiment", blank=True, null=True)
    contrat_location = models.ForeignKey(ContratLocation, blank=True, null=True)
    entrepreneur = models.ForeignKey(Professionnel, blank=True, null=True)
    societe = models.ForeignKey(Societe, blank=True, null=True)
    description = models.TextField()
    montant = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    date_realisation = models.DateField(auto_now=False,
                                        auto_now_add=False,
                                        blank=True,
                                        null=True,
                                        verbose_name=u"Date réalisation")

    @staticmethod
    def find_by_batiment(batiment_id):
        batiment = Batiment.find_batiment(batiment_id)
        return FraisMaintenance.objects.all()

    @staticmethod
    def find_my_frais():
        batiments = Batiment.find_my_batiments()
        frais = []
        n = timezone.now()
        for b in batiments:
            frais_liste = FraisMaintenance.find_by_batiment(b.id)
            for f in frais_liste:
                if f.contrat_location is None and f.date_realisation is not None \
                        and (f.date_realisation.month == n.month and f.date_realisation.year == n.year):
                    if f not in frais:
                        frais.append(f)
        return frais

    def __str__(self):
        ch = ""

        if self.description:
            ch = ch + "" + self.description
        return ch


class SuiviLoyer(models.Model):
    ETAT = (
        ('A_VERIFIER', 'A vérifier'),
        ('IMPAYE', 'Impayé'),
        ('EN_RETARD', 'En retard'),
        ('PAYE', 'Payé')
    )

    financement_location = models.ForeignKey(FinancementLocation)
    date_paiement = models.DateField(auto_now=False, auto_now_add=False)
    etat_suivi = models.CharField(max_length=10, choices=ETAT, default='A_VERIFIER')
    remarque = models.TextField(blank=True, null=True)
    loyer_percu = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    charges_percu = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    date_paiement_reel = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['date_paiement']

    @staticmethod
    def find_suivis(date_d_param, date_f_param, etat_param):
        etat = None
        if etat_param != "":
            etat = etat_param
        date_d = None
        if date_d_param != "":
            date_d = date_d_param
        date_f = None
        if date_f_param != "":
            date_f = date_f_param
        out = None
        queryset = SuiviLoyer.objects
        if etat:
            queryset = queryset.filter(etat_suivi=etat)
        if date_d:
            queryset = queryset.filter(date_paiement__gte=date_d)
        if date_f:
            queryset = queryset.filter(date_paiement__lte=date_f)
        if etat or date_d or date_f:
            out = queryset
        return out

    @staticmethod
    def find_suivis_a_verifier():
        return SuiviLoyer.objects.filter(Q(date_paiement__gte=timezone.now(),
                                           date_paiement__lte=timezone.now() + relativedelta(months=1),
                                           etat_suivi='A_VERIFIER')
                                         | Q(date_paiement__lte=timezone.now(), etat_suivi='A_VERIFIER'))

    @staticmethod
    def find_suivis_a_verifier_proche():
        return SuiviLoyer.objects.filter(Q(date_paiement__lte=timezone.now() + relativedelta(months=2),
                                           etat_suivi='A_VERIFIER'))

    @staticmethod
    def find_suivis_by_etat_suivi(date_ref, etat_suivi):
        start_date = datetime.datetime(date_ref.year, date_ref.month, 1)
        end_date = datetime.datetime(date_ref.year, date_ref.month, calendar.mdays[date_ref.month])
        return SuiviLoyer.objects.filter(date_paiement__lte=end_date, date_paiement__gte=start_date,
                                         etat_suivi=etat_suivi)

    @staticmethod
    def find_mes_suivis_by_etat_suivi(date_ref, etat_suivi):
        mes_batiment = Batiment.find_my_batiments()
        start_date = datetime.datetime(date_ref.year, date_ref.month, 1)
        end_date = datetime.datetime(date_ref.year, date_ref.month, calendar.mdays[date_ref.month])
        return SuiviLoyer.objects.filter(date_paiement__lte=end_date, date_paiement__gte=start_date,
                                         etat_suivi=etat_suivi,
                                         financement_location__contrat_location__batiment__in=mes_batiment)

    @staticmethod
    def find_suivis_by_pas_etat_suivi(date_ref, etat_suivi):
        start_date = datetime.datetime(date_ref.year, date_ref.month, 1)
        end_date = datetime.datetime(date_ref.year, date_ref.month, calendar.mdays[date_ref.month])
        return SuiviLoyer.objects.filter(date_paiement__lte=end_date, date_paiement__gte=start_date)\
            .exclude(etat_suivi=etat_suivi)

    @staticmethod
    def find_all():
        return SuiviLoyer.objects.all()

    def __str__(self):
        desc = ""
        if self.date_paiement:
            desc += self.date_paiement.strftime('%d-%m-%Y')

        if self.remarque:
            desc += " , (" + self.remarque + ")"

        if self.etat_suivi:
            desc += " (" + self.etat_suivi + ")"
        return desc

    @staticmethod
    def find_suivis_paye(financement):
        # return SuiviLoyer.objects.filter(financement_location = financement, etat_suivi='PAYE')
        return SuiviLoyer.objects.all()


class ContratGestion(models.Model):
    batiment = models.ForeignKey(Batiment)
    gestionnaire = models.ForeignKey(Personne)
    date_debut = models.DateField(auto_now=False,  auto_now_add=False, blank=True, null=True)
    date_fin = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    montant_mensuel = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    @staticmethod
    def find_all():
        return ContratGestion.objects.all()

    @staticmethod
    def find_my_contrats():
        personne = Personne.find_gestionnaire_default()
        return ContratGestion.objects.filter(gestionnaire=personne)

    @staticmethod
    def search(batiment, date_debut, date_fin):
        out = None
        queryset = ContratGestion.objects
        if batiment:
            queryset = queryset.filter(batiment=batiment)
        if date_debut:
            queryset = queryset.filter(date_debut_lte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_fin_gte=date_fin)
        if batiment or date_debut or date_fin:
            out = queryset
        return out

    def __str__(self):
        return self.gestionnaire.nom + ", " + self.gestionnaire.prenom + str(self.batiment)

    def save(self,  *args, **kwargs):

        c = super(ContratGestion, self).save(*args, **kwargs)

        if self.date_fin:
            alert = Alerte(description='Attention fin contrat location dans 4 mois',
                           date_alerte=self.date_fin - relativedelta(months=4), etat='A_VERIFIER', contrat_gestion=self)
            alert.save()
        if self.date_debut and self.date_fin:
            date_d = self.date_debut
            date_f = self.date_debut + relativedelta(months=1)
            i = 0
            while date_f <= self.date_fin:
                honoraire = Honoraire(etat='A_VERIFIER', contrat_gestion=self, date_paiement=date_d)
                honoraire.save()
                date_d = date_d + relativedelta(months=1)
                date_f = date_f + relativedelta(months=1)
                i = i + 1

        return c


class ModeleDocument(models.Model):
    # TYPE_DOCUMENT = (
        # ('LETTRE_INDEXATION', 'Lettre indexation'),
    # )
    type_document = models.CharField(max_length=50)
    contenu = models.TextField()

    def __str__(self):
        return self.type_document


class Alerte(models.Model):
    ETAT = (
        ('A_VERIFIER', 'A vérifier'),
        ('VERIFIER', 'Vérifier'),
        ('COURRIER', 'Courrier à préparer'))

    description = models.TextField(verbose_name=u"Description")
    date_alerte = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                                   verbose_name=u"Date alerte")
    contrat_gestion = models.ForeignKey(ContratGestion, blank=True, null=True, verbose_name=u"Contrat de gestion")
    contrat_location = models.ForeignKey(ContratLocation, blank=True, null=True, verbose_name=u"Contrat location")
    etat = models.CharField(max_length=10, choices=ETAT, default='A_VERIFIER', verbose_name=u"Etat")

    class Meta:
        ordering = ['date_alerte']

    @staticmethod
    def find_by_etat(etat_alerte):
        return Alerte.objects.filter(etat=etat_alerte)

    @staticmethod
    def find_by_etat_today(etat_alerte):
        date_d = timezone.now() - relativedelta(months=1)
        date_f = timezone.now() + relativedelta(months=1)
        return Alerte.objects.filter(etat=etat_alerte, date_alerte__lte=date_f, date_alerte__gte=date_d)

    def __str__(self):
        return self.date_alerte.strftime('%d-%m-%Y') + " " + self.etat


class Pays(models.Model):
    pays = models.CharField(max_length=50)


class Honoraire(models.Model):
    ETAT_HONORAIRE = (
        ('A_VERIFIER', 'A vérifier'),
        ('IMPAYE', 'Impayé'),
        ('EN_RETARD', 'En retard'),
        ('PAYE', 'Payé')
    )
    contrat_gestion = models.ForeignKey(ContratGestion, blank=True, null=True, verbose_name=u"Contrat de gestion")
    date_paiement = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                                     verbose_name=u"Date paiement")
    etat = models.CharField(max_length=10, choices=ETAT_HONORAIRE, default='A_VERIFIER', verbose_name=u"Etat")

    @staticmethod
    def find_honoraires_by_etat_today(etat):
        date_d = timezone.now() - relativedelta(months=1)
        date_f = timezone.now() + relativedelta(months=1)
        return Honoraire.objects.filter(etat=etat, date_paiement__lte=date_f, date_paiement__gte=date_d)

    @staticmethod
    def find_all():
        return Honoraire.objects.all()

    @staticmethod
    def find_by_batiment_etat_date(batiment_id, etat, date_limite_inf):
        queryset = Honoraire.objects

        if batiment_id:
            queryset = queryset.filter(contrat_gestion__batiment__id=int(batiment_id))

        if etat is not None and len(etat) > 0:
            queryset = queryset.filter(etat=etat)

        if date_limite_inf:
            queryset = queryset.filter(date_paiement__gte=date_limite_inf)

        return queryset

    @staticmethod
    def find_all_batiments():
        batiments = []
        for c in ContratGestion.find_all():
            if c.batiment not in batiments:
                batiments.append(c.batiment)
        return batiments

    def __str__(self):
        if self.contrat_gestion:
            return str(self.contrat_gestion)
        else:
            return ""


class Photo(models.Model):
    photo = models.FileField(upload_to="photos")
    texte = models.TextField(default="")

    def __str__(self):
        return self.texte


def update_suivi_alerte(date_debut, location, financement_location, date_fin, type_suivi):
    date_d = date_debut
    date_f = date_debut + relativedelta(months=1)
    i = 0
    while date_f <= date_fin:
        print(' creation nouveau suivi')
        suivi = SuiviLoyer(etat_suivi='A_VERIFIER',
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
        alert = Alerte(description='Attention fin contrat location dans 4 mois',
                       date_alerte=location.date_fin - relativedelta(months=4),
                       etat='A_VERIFIER',
                       contrat_location=location)
        alert.save()


