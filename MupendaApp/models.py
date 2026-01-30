import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django_ckeditor_5.fields import CKEditor5Field

STATUS = ((0,"Draft "), (1,"Publié "))

#Table Categorie

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    update_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    is_administrateur = models.BooleanField(default=False)
    is_utilisateur = models.BooleanField(default=True)
    photo_profil = models.ImageField(upload_to="static/images", blank=True, null=True)

#Table Contact

class Contact(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, null=True)

#Table Formation

class Formation(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    description = CKEditor5Field(null=True)
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    date_debut = models.DateField(null=True)
    date_fin = models.DateField(null=True)
    heure_debut = models.TimeField(null=True)
    heure_fin = models.TimeField(null=True)
    prix = models.FloatField(default=0, null=True)
    formateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='formation_post'
    )
    categorie = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    update_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return self.nom

#Table Apropos

class Apropos(models.Model):
    nom = models.CharField(max_length=255, unique=True, null=True)
    contenus = CKEditor5Field(null=True)
    photo = models.ImageField(upload_to="static/images", blank=True, null=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='apropos',
        null=True
    )
    date_ajout = models.DateTimeField(auto_now=True)
    update_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_ajout']

    def __str__(self):
        return self.nom

#Table Services

class Services(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    description = CKEditor5Field(null=True)
    photo = models.ImageField(upload_to="static/images", blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_ajout']

    def __str__(self):
        return self.nom

#Table Realisation

class Realisation(models.Model):
    titre = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    description = CKEditor5Field(null=True)
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='realisation',
        null=True
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(choices=STATUS, default=0)
    created_on = models.DateTimeField(auto_now_add=True, null= True)
    update_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre
    
# Table Temoignage

class TemoignageClient(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, null=True)
    message = CKEditor5Field(null=True)
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='temoignage_client',
        null=True
    )
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    update_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)

    def __str__(self):
        return self.nom

# table Blog

class Post(models.Model):
    titre = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='blog_posts'
        )
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)
    content = CKEditor5Field()
    categorie = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(choices=STATUS, default=0)
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    # pays = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.titre
    
@receiver(pre_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# fin table blog

# Table Arsenal / Equipements

class Equipement(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    model = models.CharField(max_length=250, null=True)
    marque = models.CharField(max_length=250, null=True)
    color = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name='equipement'
    )
    autres_details = models.CharField(max_length=1000, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.name
    
# Table Formateur
class Formateur(models.Model):
    SEX_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin')
    ]
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1, choices=SEX_CHOICES, default='M')
    age = models.IntegerField(default=18)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    addresse = models.CharField(max_length=255, default="Goma/Nord-Kivu")
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    specialite = models.CharField(max_length=250, default="Formateur")
    # module = models.ForeignKey()
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)

# Table Client
class Client(models.Model):
    TYPE_CLIENT_CHOICES = [
        ('PME', 'PME'),
        ('STARTUP', 'Startup'),
        ('GRAND_COMPTE', 'Grand Compte'),
        ('PARTICULIER', 'Particulier'),
    ]
    
    STATUT_CLIENT_CHOICES = [
        ('PROSPECT', 'Prospect'),
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('ARCHIVE', 'Archivé'),
    ]
    
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    type_client = models.CharField(max_length=20, choices=TYPE_CLIENT_CHOICES, default='PARTICULIER')
    statut_client = models.CharField(max_length=20, choices=STATUT_CLIENT_CHOICES, default='PROSPECT')
    siret = models.CharField(max_length=14, blank=True, null=True, help_text="Numéro SIRET pour les entreprises")
    secteur_activite = models.CharField(max_length=100, blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    responsable_compte = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clients_geres'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Client"
        verbose_name_plural = "Clients"
    
    def __str__(self):
        return f"{self.nom} ({self.type_client})"
    
    def get_nombre_projets(self):
        return self.associations_projet.count()
    
    def get_derniere_interaction(self):
        return self.interactions.order_by('-date_interaction').first()

# Table HistoriqueInteraction
class HistoriqueInteraction(models.Model):
    TYPE_INTERACTION_CHOICES = [
        ('APPEL', 'Appel téléphonique'),
        ('EMAIL', 'Email'),
        ('RENDEZ_VOUS', 'Rendez-vous'),
        ('REUNION', 'Réunion'),
        ('DEMONSTRATION', 'Démonstration'),
        ('PROPOSITION', 'Proposition commerciale'),
        ('SUIVI', 'Suivi'),
        ('AUTRE', 'Autre'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions')
    type_interaction = models.CharField(max_length=20, choices=TYPE_INTERACTION_CHOICES)
    date_interaction = models.DateTimeField()
    duree_minutes = models.IntegerField(null=True, blank=True, help_text="Durée en minutes")
    sujet = models.CharField(max_length=200)
    description = CKEditor5Field(blank=True, null=True)
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interactions_realisees'
    )
    prochain_rappel = models.DateTimeField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_interaction']
        verbose_name = "Historique d'interaction"
        verbose_name_plural = "Historique des interactions"
    
    def __str__(self):
        return f"{self.client.nom} - {self.type_interaction} - {self.date_interaction.strftime('%d/%m/%Y')}"

# Table AssociationClientProjet
class AssociationClientProjet(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='associations_projet')
    projet = models.ForeignKey(Realisation, on_delete=models.CASCADE, related_name='associations_client')
    role_dans_projet = models.CharField(max_length=100, default="Client")
    budget_alloue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_debut_association = models.DateField()
    date_fin_association = models.DateField(null=True, blank=True)
    statut_association = models.CharField(
        max_length=20,
        choices=[
            ('EN_COURS', 'En cours'),
            ('TERMINE', 'Terminé'),
            ('SUSPENDU', 'Suspendu'),
            ('ANNULE', 'Annulé'),
        ],
        default='EN_COURS'
    )
    notes_association = models.TextField(blank=True, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['client', 'projet']
        ordering = ['-date_debut_association']
        verbose_name = "Association Client-Projet"
        verbose_name_plural = "Associations Clients-Projets"
    
    def __str__(self):
        return f"{self.client.nom} ↔ {self.projet.titre}"

# Table Projet
class Projet(models.Model):
    TYPE_PROJET_CHOICES = [
        ('FORFAIT', 'Forfait'),
        ('REGIE', 'Régie'),
        ('MAINTENANCE', 'Maintenance'),
        ('CONSULTING', 'Consulting'),
    ]
    
    STATUT_PROJET_CHOICES = [
        ('PLANIFICATION', 'Planification'),
        ('EN_COURS', 'En cours'),
        ('SUSPENDU', 'Suspendu'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    nom = models.CharField(max_length=200)
    description = CKEditor5Field()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projets')
    date_debut = models.DateField()
    date_fin = models.DateField()
    date_fin_reelle = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_PROJET_CHOICES, default='PLANIFICATION')
    type_projet = models.CharField(max_length=20, choices=TYPE_PROJET_CHOICES, default='FORFAIT')
    budget_initial = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_consomme = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    chef_projet = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projets_geres'
    )
    priorite = models.CharField(
        max_length=10,
        choices=[
            ('BASSE', 'Basse'),
            ('MOYENNE', 'Moyenne'),
            ('HAUTE', 'Haute'),
            ('CRITIQUE', 'Critique'),
        ],
        default='MOYENNE'
    )
    progression = models.IntegerField(default=0, help_text="Progression en pourcentage")
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-cree_le']
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
    
    def __str__(self):
        return f"{self.nom} - {self.client.nom}"
    
    def get_nombre_collaborateurs(self):
        return self.affectations.count()
    
    def get_duree_jours(self):
        if self.date_fin_reelle:
            return (self.date_fin_reelle - self.date_debut).days
        return (self.date_fin - self.date_debut).days
    
    def get_jours_ecoules(self):
        return (timezone.now().date() - self.date_debut).days
    
    def get_budget_restant(self):
        if self.budget_initial:
            return self.budget_initial - self.budget_consomme
        return None
    
    def est_en_retard(self):
        if self.statut in ['EN_COURS', 'SUSPENDU']:
            return timezone.now().date() > self.date_fin
        return False
    
    def get_temps_total_saisi(self):
        """Retourne le temps total saisi en heures pour ce projet"""
        total = self.suivi_temps.aggregate(total=models.Sum('heures'))['total'] or 0
        return total

# Table AffectationCollaborateur
class AffectationCollaborateur(models.Model):
    ROLE_CHOICES = [
        ('CHEF_PROJET', 'Chef de projet'),
        ('DEVELOPPEUR', 'Développeur'),
        ('DESIGNER', 'Designer'),
        ('TESTEUR', 'Testeur'),
        ('CONSULTANT', 'Consultant'),
        ('ANALYSTE', 'Analyste'),
        ('AUTRE', 'Autre'),
    ]
    
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='affectations')
    collaborateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='affectations_projet'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEVELOPPEUR')
    date_affectation = models.DateField(auto_now_add=True)
    date_fin_affectation = models.DateField(null=True, blank=True)
    taux_horaire = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    est_actif = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['projet', 'collaborateur']
        ordering = ['-date_affectation']
        verbose_name = "Affectation collaborateur"
        verbose_name_plural = "Affectations collaborateurs"
    
    def __str__(self):
        return f"{self.collaborateur.username} - {self.role} sur {self.projet.nom}"

# Table SuiviTemps
class SuiviTemps(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validé'),
        ('REJETE', 'Rejeté'),
    ]
    
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='suivi_temps')
    collaborateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='temps_saisi'
    )
    date_saisie = models.DateField()
    heures = models.DecimalField(max_digits=5, decimal_places=2, help_text="Nombre d'heures travaillées")
    description = models.TextField(help_text="Description du travail effectué")
    type_travail = models.CharField(
        max_length=20,
        choices=[
            ('DEVELOPPEMENT', 'Développement'),
            ('ANALYSE', 'Analyse'),
            ('TEST', 'Test'),
            ('REUNION', 'Réunion'),
            ('DOCUMENTATION', 'Documentation'),
            ('MAINTENANCE', 'Maintenance'),
            ('AUTRE', 'Autre'),
        ],
        default='DEVELOPPEMENT'
    )
    taux_horaire = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Taux horaire pour calcul du montant")
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Montant calculé automatiquement")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    commentaire_validation = models.TextField(null=True, blank=True, help_text="Commentaire du validateur")
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validations_temps'
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_saisie']
        verbose_name = "Suivi du temps"
        verbose_name_plural = "Suivis du temps"
    
    def __str__(self):
        return f"{self.heures}h - {self.collaborateur.username} - {self.projet.nom}"
    
    def save(self, *args, **kwargs):
        # Calcul automatique du montant
        if self.taux_horaire and self.heures:
            self.montant = self.heures * self.taux_horaire
        super().save(*args, **kwargs)

# FACTURATION
class Devis(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('ENVOYE', 'Envoyé'),
        ('ACCEPTE', 'Accepté'),
        ('REFUSE', 'Refusé'),
        ('EXPIRE', 'Expiré'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devis')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='devis', null=True, blank=True)
    date_emission = models.DateField(auto_now_add=True)
    date_validite = models.DateField()
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='BROUILLON')
    notes = models.TextField(blank=True)
    conditions_paiement = models.TextField(default="Paiement à 30 jours")
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='devis_crees'
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_emission']
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
    
    def __str__(self):
        return f"Devis {self.numero} - {self.client.nom}"
    
    def save(self, *args, **kwargs):
        # Calcul du montant TTC
        self.montant_ttc = self.montant_ht + self.montant_tva
        super().save(*args, **kwargs)
    
    def generer_numero(self):
        from datetime import datetime
        annee = datetime.now().year
        dernier = Devis.objects.filter(numero__startswith=f'DEV{annee}').order_by('-numero').first()
        if dernier:
            numero = int(dernier.numero[7:]) + 1
        else:
            numero = 1
        return f'DEV{annee}{numero:04d}'

class Facture(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('ENVOYEE', 'Envoyée'),
        ('PAYEE', 'Payée'),
        ('EN_RETARD', 'En retard'),
        ('ANNULEE', 'Annulée'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    devis = models.OneToOneField(Devis, on_delete=models.SET_NULL, null=True, blank=True, related_name='facture')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='factures')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='factures', null=True, blank=True)
    date_emission = models.DateField(auto_now_add=True)
    date_echeance = models.DateField()
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='BROUILLON')
    date_paiement = models.DateField(null=True, blank=True)
    mode_paiement = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='factures_crees'
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_emission']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
    
    def __str__(self):
        return f"Facture {self.numero} - {self.client.nom}"
    
    def save(self, *args, **kwargs):
        # Calcul du montant TTC
        self.montant_ttc = self.montant_ht + self.montant_tva
        if not self.date_echeance:
            from datetime import timedelta
            self.date_echeance = self.date_emission + timedelta(days=30)
        super().save(*args, **kwargs)
    
    def generer_numero(self):
        from datetime import datetime
        annee = datetime.now().year
        dernier = Facture.objects.filter(numero__startswith=f'FAC{annee}').order_by('-numero').first()
        if dernier:
            numero = int(dernier.numero[7:]) + 1
        else:
            numero = 1
        return f'FAC{annee}{numero:04d}'
    
    def est_en_retard(self):
        from datetime import date
        return self.statut != 'PAYEE' and self.date_echeance < date.today()

class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    description = models.CharField(max_length=200)
    quantite = models.DecimalField(max_digits=8, decimal_places=2)
    prix_unitaire_ht = models.DecimalField(max_digits=10, decimal_places=2)
    total_ht = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
    
    def __str__(self):
        return f"{self.description} - {self.facture.numero}"
    
    def save(self, *args, **kwargs):
        self.total_ht = self.quantite * self.prix_unitaire_ht
        super().save(*args, **kwargs)

# GESTION DES COLLABORATEURS
class Collaborateur(models.Model):
    POSTE_CHOICES = [
        ('DEVELOPPEUR', 'Développeur'),
        ('DESIGNEUR', 'Designer'),
        ('MANAGER', 'Manager'),
        ('CONSULTANT', 'Consultant'),
        ('TESTEUR', 'Testeur'),
        ('COMMERCIAL', 'Commercial'),
        ('AUTRE', 'Autre'),
    ]
    
    DISPO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('OCCUPE', 'Occupé'),
        ('CONGE', 'Congé'),
        ('INDISPONIBLE', 'Indisponible'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_collaborateur'
    )
    poste = models.CharField(max_length=50, choices=POSTE_CHOICES)
    tjm = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="TJM journalier (€)")
    cout_horaire = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Coût horaire (€)")
    disponibilite = models.CharField(max_length=20, choices=DISPO_CHOICES, default='DISPONIBLE')
    competences = models.TextField(help_text="Compétences principales")
    date_embauche = models.DateField()
    telephone = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    photo = models.ImageField(upload_to='collaborateurs/', blank=True)
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Collaborateur"
        verbose_name_plural = "Collaborateurs"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.poste}"
    
    def get_projets_actifs(self):
        return self.user.affectations.filter(est_actif=True).values_list('projet__nom', flat=True)
    
    def get_taux_occupation(self):
        total_projets = self.user.affectations.filter(est_actif=True).count()
        return f"{total_projets} projet(s) actif(s)"

# SUPPORT CLIENT
class TicketSupport(models.Model):
    STATUT_CHOICES = [
        ('OUVERT', 'Ouvert'),
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
        ('FERME', 'Fermé'),
        ('URGENT', 'Urgent'),
    ]
    
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('NORMALE', 'Normale'),
        ('HAUTE', 'Haute'),
        ('URGENTE', 'Urgente'),
    ]
    
    TYPE_CHOICES = [
        ('TECHNIQUE', 'Technique'),
        ('FACTURATION', 'Facturation'),
        ('COMMERCIAL', 'Commercial'),
        ('AUTRE', 'Autre'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_demande = models.CharField(max_length=20, choices=TYPE_CHOICES, default='TECHNIQUE')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='NORMALE')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='OUVERT')
    assigne_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_assignes'
    )
    projet_concerne = models.ForeignKey(Projet, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tickets_crees'
    )
    resolu_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_resolus'
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Ticket support"
        verbose_name_plural = "Tickets support"
    
    def __str__(self):
        return f"Ticket {self.numero} - {self.titre}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generer_numero()
        if self.statut == 'RESOLU' and not self.date_resolution:
            from django.utils import timezone
            self.date_resolution = timezone.now()
        super().save(*args, **kwargs)
    
    def generer_numero(self):
        from datetime import datetime
        annee = datetime.now().year
        dernier = TicketSupport.objects.filter(numero__startswith=f'TKT{annee}').order_by('-numero').first()
        if dernier:
            numero = int(dernier.numero[7:]) + 1
        else:
            numero = 1
        return f'TKT{annee}{numero:04d}'
    
    def get_duree_resolution(self):
        if self.date_resolution:
            from datetime import timedelta
            duree = self.date_resolution - self.date_creation
            return duree.days
        return None

class MessageTicket(models.Model):
    ticket = models.ForeignKey(TicketSupport, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_message = models.DateTimeField(auto_now_add=True)
    est_interne = models.BooleanField(default=False, help_text="Visible uniquement par l'équipe")
    
    class Meta:
        ordering = ['date_message']
        verbose_name = "Message ticket"
        verbose_name_plural = "Messages tickets"
    
    def __str__(self):
        return f"Message de {self.auteur.username} - {self.ticket.numero}" 
