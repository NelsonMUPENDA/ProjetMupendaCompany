import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone

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
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_embauche = models.DateField(blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    derniere_connexion = models.DateTimeField(blank=True, null=True)
    tentative_echec = models.IntegerField(default=0)
    bloque_jusqua = models.DateTimeField(blank=True, null=True)
    
    # Préférences utilisateur stockées en base de données
    pref_email_notifications = models.BooleanField(default=True, verbose_name="Notifications par email")
    pref_dark_mode = models.BooleanField(default=False, verbose_name="Mode sombre")

    def __str__(self):
        return f"{self.username} ({self.get_primary_role()})"

    def get_primary_role(self):
        """Retourne le rôle principal de l'utilisateur"""
        user_role = self.user_roles.filter(est_actif=True).first()
        return user_role.role.nom if user_role else "Aucun rôle"

    def has_permission(self, permission_code):
        """Vérifie si l'utilisateur a une permission spécifique"""
        return self.user_roles.filter(
            role__permissions__code=permission_code,
            est_actif=True
        ).exists()

    def is_super_admin(self):
        """Vérifie si l'utilisateur est Super Admin"""
        return self.user_roles.filter(
            role__nom='SUPER_ADMIN',
            est_actif=True
        ).exists()

    def is_admin(self):
        """Vérifie si l'utilisateur est Administrateur"""
        return self.user_roles.filter(
            role__nom='ADMINISTRATEUR',
            est_actif=True
        ).exists()

    def can_access_super_admin_dashboard(self):
        """Vérifie si l'utilisateur peut accéder au dashboard Super Admin"""
        return self.is_super_admin()

    def can_access_admin_dashboard(self):
        """Vérifie si l'utilisateur peut accéder au dashboard Admin"""
        return self.is_admin() or self.is_super_admin()

    def is_banned(self):
        """Vérifie si l'utilisateur est banni"""
        return not self.est_actif or (self.bloque_jusqua and self.bloque_jusqua > timezone.now())


# Modèles de gestion des rôles et permissions
class Permission(models.Model):
    """Modèle pour les permissions du système"""
    CATEGORIES = [
        ('UTILISATEUR', 'Gestion des utilisateurs'),
        ('ROLE', 'Gestion des rôles'),
        ('DEPARTEMENT', 'Gestion des départements'),
        ('PROJET', 'Gestion des projets'),
        ('TACHE', 'Gestion des tâches'),
        ('CLIENT', 'Gestion des clients'),
        ('FACTURATION', 'Gestion de la facturation'),
        ('CONTENU', 'Gestion du contenu'),
        ('RAPPORT', 'Accès aux rapports'),
        ('SYSTEME', 'Administration système'),
        ('SUPPORT', 'Gestion du support'),
        ('FORMATION', 'Gestion des formations'),
    ]
    
    code = models.CharField(max_length=100, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    est_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['categorie', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.categorie})"

class Role(models.Model):
    """Modèle pour les rôles du système"""
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Administrateur'),
        ('ADMINISTRATEUR', 'Administrateur'),
        ('CHEF_PROJET', 'Chef de Projet'),
        ('DEVELOPPEUR', 'Développeur'),
        ('DESIGNER', 'Designer'),
        ('COMMERCIAL', 'Commercial'),
        ('COMPTABLE', 'Comptable'),
        ('RH', 'Ressources Humaines'),
        ('SUPPORT', 'Support Technique'),
        ('CLIENT', 'Client'),
        ('COLLABORATEUR', 'Collaborateur'),
        ('FORMATEUR', 'Formateur'),
        ('STAGIAIRE', 'Stagiaire'),
    ]
    
    nom = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    niveau_hierarchique = models.IntegerField(default=0)  # 0 = plus bas, 10 = plus haut
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')
    
    class Meta:
        ordering = ['-niveau_hierarchique', 'nom']
    
    def __str__(self):
        return f"{self.get_nom_display()} (Niveau {self.niveau_hierarchique})"

class UserRole(models.Model):
    """Modèle d'association entre utilisateur et rôle"""
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    date_attribution = models.DateTimeField(auto_now_add=True)
    attribue_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='attributions')
    est_actif = models.BooleanField(default=True)
    date_expiration = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['utilisateur', 'role']
        ordering = ['-date_attribution']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.role.nom}"
    
    def is_expired(self):
        """Vérifie si le rôle est expiré"""
        if self.date_expiration:
            return timezone.now() > self.date_expiration
        return False

# Modèles pour la gestion d'entreprise
class Departement(models.Model):
    """Modèle pour les départements de l'entreprise"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    responsable = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='departements_responsables')
    couleur = models.CharField(max_length=7, default="#FF6700")  # Couleur hexadécimale
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nom']
        verbose_name = "Département"
        verbose_name_plural = "Départements"
    
    def __str__(self):
        return self.nom

class Projet(models.Model):
    """Modèle pour les projets de l'entreprise"""
    STATUT_CHOICES = [
        ('PLANIFICATION', 'Planification'),
        ('EN_COURS', 'En cours'),
        ('EN_PAUSE', 'En pause'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('URGENTE', 'Urgente'),
    ]
    
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    client = models.CharField(max_length=200, blank=True, null=True)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='projets', null=True, blank=True)
    chef_projet = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='projets_chef')
    equipe = models.ManyToManyField(CustomUser, blank=True, related_name='projets_equipe')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PLANIFICATION')
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='MOYENNE')
    date_debut = models.DateField()
    date_fin_prevue = models.DateField(default=timezone.now)
    date_fin_reelle = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    progression = models.IntegerField(default=0, help_text="Pourcentage de progression (0-100)")
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='projets_crees')
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
    
    def __str__(self):
        return f"{self.nom} ({self.statut})"
    
    def get_progression_color(self):
        """Retourne la couleur en fonction de la progression"""
        if self.progression < 25:
            return "#dc3545"  # Rouge
        elif self.progression < 50:
            return "#ffc107"  # Jaune
        elif self.progression < 75:
            return "#fd7e14"  # Orange
        else:
            return "#28a745"  # Vert
    
    def get_jours_restants(self):
        """Calcule le nombre de jours restants avant la fin prévue"""
        if self.date_fin_prevue:
            delta = self.date_fin_prevue - timezone.now().date()
            return max(0, delta.days)
        return 0

class Tache(models.Model):
    """Modèle pour les tâches des projets"""
    STATUT_CHOICES = [
        ('A_FAIRE', 'À faire'),
        ('EN_COURS', 'En cours'),
        ('EN_REVISION', 'En révision'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('URGENTE', 'Urgente'),
    ]
    
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='taches')
    assigne_a = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='taches_assignees')
    cree_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='taches_crees')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='A_FAIRE')
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='MOYENNE')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField(blank=True, null=True)
    date_terminee = models.DateTimeField(blank=True, null=True)
    temps_estime = models.IntegerField(blank=True, null=True, help_text="Temps estimé en heures")
    temps_passe = models.IntegerField(default=0, help_text="Temps passé en heures")
    progression = models.IntegerField(default=0, help_text="Pourcentage de progression (0-100)")
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
    
    def __str__(self):
        return f"{self.titre} ({self.statut})"
    
    def get_priorite_color(self):
        """Retourne la couleur en fonction de la priorité"""
        colors = {
            'BASSE': '#28a745',
            'MOYENNE': '#ffc107',
            'HAUTE': '#fd7e14',
            'URGENTE': '#dc3545'
        }
        return colors.get(self.priorite, '#6c757d')
    
    def est_en_retard(self):
        """Vérifie si la tâche est en retard"""
        if self.date_echeance and self.statut not in ['TERMINE', 'ANNULE']:
            return timezone.now().date() > self.date_echeance
        return False

class Notification(models.Model):
    """Modèle pour les notifications du système"""
    TYPE_CHOICES = [
        ('INFO', 'Information'),
        ('SUCCES', 'Succès'),
        ('AVERTISSEMENT', 'Avertissement'),
        ('ERREUR', 'Erreur'),
        ('TACHE', 'Tâche'),
        ('PROJET', 'Projet'),
        ('SYSTEME', 'Système'),
    ]
    
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES, default='INFO')
    destinataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    est_lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(blank=True, null=True)
    lien = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire.username}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        self.est_lue = True
        self.date_lecture = timezone.now()
        self.save()

class LogAction(models.Model):
    """Modèle pour les logs d'actions des utilisateurs"""
    ACTION_CHOICES = [
        ('CREATION', 'Création'),
        ('MODIFICATION', 'Modification'),
        ('SUPPRESSION', 'Suppression'),
        ('CONNEXION', 'Connexion'),
        ('DECONNEXION', 'Déconnexion'),
        ('VISUALISATION', 'Visualisation'),
        ('EXPORTATION', 'Exportation'),
        ('AUTRE', 'Autre'),
    ]
    
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='logs_actions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    modele = models.CharField(max_length=100, blank=True, null=True)
    id_objet = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    adresse_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_action']
        verbose_name = "Log d'action"
        verbose_name_plural = "Logs d'actions"
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.action} - {self.date_action}"

# Table Contact
class Contact(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, null=True)


# Table SiteContact - Informations de contact de l'entreprise
class SiteContact(models.Model):
    """Modèle pour stocker les informations de contact de l'entreprise"""
    
    # Adresse
    adresse_complete = models.TextField(
        default="Goma, République Démocratique du Congo",
        help_text="Adresse complète de l'entreprise"
    )
    
    # Coordonnées
    telephone_principal = models.CharField(
        max_length=50, 
        default="(+243) 000 000 000",
        help_text="Numéro de téléphone principal"
    )
    telephone_secondaire = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Numéro de téléphone secondaire (optionnel)"
    )
    email_principal = models.EmailField(
        max_length=100,
        default="contact@mupenda.cd",
        help_text="Email principal de contact"
    )
    email_support = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Email pour le support client"
    )
    
    # Horaires d'ouverture
    horaires_ouverture = models.CharField(
        max_length=255,
        default="Lundi - Samedi : 08h00 - 16h00",
        help_text="Horaires d'ouverture (texte libre)"
    )
    
    # Réseaux sociaux (optionnels)
    facebook_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de la page Facebook"
    )
    twitter_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de la page Twitter/X"
    )
    linkedin_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de la page LinkedIn"
    )
    instagram_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de la page Instagram"
    )
    
    # Carte/Localisation
    carte_embed_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL embed Google Maps (iframe)"
    )
    
    # Métadonnées
    est_actif = models.BooleanField(
        default=True,
        help_text="Si coché, ces informations seront affichées sur le site"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Information de Contact"
        verbose_name_plural = "Informations de Contact"
    
    def __str__(self):
        return f"Contact - {self.email_principal} ({self.telephone_principal})"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'un seul enregistrement actif
        if self.est_actif:
            SiteContact.objects.filter(est_actif=True).exclude(pk=self.pk).update(est_actif=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_contact_actif(cls):
        """Récupère les informations de contact actives"""
        return cls.objects.filter(est_actif=True).first()


class Apropos(models.Model):
    """Modèle complet pour la page À propos - contient toutes les sections dynamiques"""
    
    # Section Header
    titre_page = models.CharField(max_length=255, default="Qui sommes-nous ?")
    sous_titre_page = models.TextField(
        default="Découvrez Mupenda Company, votre partenaire technologique de confiance en RDC et en Afrique."
    )
    
    # Section Principale (About)
    nom_entreprise = models.CharField(max_length=255, default="Mupenda Company")
    description_entreprise = CKEditor5Field(null=True, blank=True)
    photo_principale = models.ImageField(upload_to="static/images/apropos", blank=True, null=True)
    
    # Statistiques
    annee_experience = models.IntegerField(default=10)
    label_annee_experience = models.CharField(max_length=50, default="Années d'expérience")
    nombre_projets = models.IntegerField(default=500)
    label_projets = models.CharField(max_length=50, default="Projets réalisés")
    nombre_clients = models.IntegerField(default=200)
    label_clients = models.CharField(max_length=50, default="Clients satisfaits")
    
    # Section Valeurs - Objectifs
    titre_objectifs = models.CharField(max_length=100, default="Nos Objectifs")
    icon_objectifs = models.CharField(max_length=50, default="bi-bullseye")
    objectif_1 = models.CharField(max_length=255, default="Créer une stratégie marketing basée sur les objectifs et les cibles du client")
    objectif_2 = models.CharField(max_length=255, default="Créer et offrir des emplois partout en RDC et en Afrique")
    objectif_3 = models.CharField(max_length=255, default="Etre une société au cœur de l'innovation congolaise et africaine")
    objectif_4 = models.CharField(max_length=255, default="Promouvoir la technologie congolaise et africaine")
    
    # Section Valeurs - Valeurs
    titre_valeurs = models.CharField(max_length=100, default="Nos Valeurs")
    icon_valeurs = models.CharField(max_length=50, default="bi-heart-fill")
    valeur_1 = models.CharField(max_length=255, default="Respect de la vie privée et dignité de nos clients")
    valeur_2 = models.CharField(max_length=255, default="Motivation et engagement dans chaque projet")
    valeur_3 = models.CharField(max_length=255, default="Créativité et innovation continue")
    valeur_4 = models.CharField(max_length=255, default="Excellence et qualité dans nos livrables")
    
    # Section Valeurs - Mission
    titre_mission = models.CharField(max_length=100, default="Notre Mission")
    icon_mission = models.CharField(max_length=50, default="bi-rocket-takeoff-fill")
    mission_1 = models.CharField(max_length=255, default="Apporter une assistance technologique et informatique aux entreprises congolaises")
    mission_2 = models.CharField(max_length=255, default="Encadrer et former les jeunes ambitieux dotés d'un esprit d'innovation")
    mission_3 = models.CharField(max_length=255, default="Contribuer à la digitalisation de l'Afrique")
    mission_4 = models.CharField(max_length=255, default="Offrir des solutions technologiques accessibles à tous")
    
    # Titre de la section valeurs
    titre_section_valeurs = models.CharField(max_length=100, default="Nos Valeurs & Objectifs")
    
    # Métadonnées
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='apropos_modifies', 
        null=True
    )
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_actif = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_modification']
        verbose_name = "Page À propos"
        verbose_name_plural = "Page À propos"
    
    def __str__(self):
        return f"À propos - {self.nom_entreprise} ({self.date_modification.strftime('%d/%m/%Y')})"
    
    def get_objectifs_list(self):
        """Retourne la liste des objectifs"""
        return [self.objectif_1, self.objectif_2, self.objectif_3, self.objectif_4]
    
    def get_valeurs_list(self):
        """Retourne la liste des valeurs"""
        return [self.valeur_1, self.valeur_2, self.valeur_3, self.valeur_4]
    
    def get_mission_list(self):
        """Retourne la liste des missions"""
        return [self.mission_1, self.mission_2, self.mission_3, self.mission_4]

class Services(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = CKEditor5Field(null=True)
    photo = models.ImageField(upload_to="static/images", blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_ajout']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


# Table Realisation
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
    created_on = models.DateTimeField(auto_now_add=True, null=True)
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
    CATEGORIE_CHOICES = [
        ('Technologie', 'Technologie'),
        ('Innovation', 'Innovation'),
        ('Business', 'Business'),
        ('Cybersécurité', 'Cybersécurité'),
        ('Cloud', 'Cloud'),
        ('IA & Data', 'IA & Data'),
        ('Actualité', 'Actualité'),
    ]
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
    category = models.CharField(max_length=50, choices=CATEGORIE_CHOICES, default='Actualité')
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

# Table FAQ
class FAQ(models.Model):
    """Modèle pour les questions fréquentes"""
    question = models.CharField(max_length=500)
    reponse = CKEditor5Field()
    categorie = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='faqs')
    ordre_affichage = models.IntegerField(default=0, help_text="Ordre d'affichage (0 = premier)")
    est_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre_affichage', 'question']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question

# Table Partenaire
class Partenaire(models.Model):
    """Modèle pour les partenaires de l'entreprise"""
    nom = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to="static/images/partenaires", blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    ordre_affichage = models.IntegerField(default=0, help_text="Ordre d'affichage sur le site")
    est_actif = models.BooleanField(default=True)
    date_debut_partenariat = models.DateField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre_affichage', 'nom']
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"

    def __str__(self):
        return self.nom 


# Table Page Legale (CGU, Politique, etc.)
class PageLegale(models.Model):
    TYPE_CHOICES = [
        ('CGU', 'Conditions Générales d\'Utilisation'),
        ('POLITIQUE', 'Politique de Confidentialité'),
        ('MENTIONS', 'Mentions Légales'),
    ]
    
    type_page = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    titre = models.CharField(max_length=255)
    sous_titre = models.CharField(max_length=500, blank=True, null=True)
    contenu = CKEditor5Field()
    derniere_mise_a_jour = models.DateField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['type_page']
        verbose_name = "Page Légale"
        verbose_name_plural = "Pages Légales"

    def __str__(self):
        return self.titre 


# Table Newsletter - Abonnés
class NewsletterSubscriber(models.Model):
    """Modèle pour les abonnés à la newsletter"""
    email = models.EmailField(max_length=255, unique=True)
    nom = models.CharField(max_length=100, blank=True, null=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_desinscription = models.DateTimeField(null=True, blank=True)
    ip_inscription = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_inscription']
        verbose_name = "Abonné Newsletter"
        verbose_name_plural = "Abonnés Newsletter"
    
    def __str__(self):
        return self.email
    
    def desinscrire(self):
        """Désinscrire l'abonné"""
        self.est_actif = False
        self.date_desinscription = timezone.now()
        self.save()


# Table Newsletter - Campagnes envoyées
class NewsletterCampaign(models.Model):
    """Modèle pour les campagnes newsletter envoyées"""
    sujet = models.CharField(max_length=255)
    contenu = CKEditor5Field()
    date_envoi = models.DateTimeField(auto_now_add=True)
    envoye_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='newsletter_campaigns'
    )
    nombre_destinataires = models.IntegerField(default=0)
    nombre_ouverts = models.IntegerField(default=0)
    est_brouillon = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_envoi']
        verbose_name = "Campagne Newsletter"
        verbose_name_plural = "Campagnes Newsletter"
    
    def __str__(self):
        return f"{self.sujet} ({self.date_envoi.strftime('%d/%m/%Y')})"


# Table Formation
class Formation(models.Model):
    """Modèle pour les formations proposées par Mupenda Company"""
    nom = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    description = CKEditor5Field(null=True)
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    date_debut = models.DateField(null=True)
    date_fin = models.DateField(null=True)
    heure_debut = models.TimeField(null=True)
    heure_fin = models.TimeField(null=True)
    prix = models.FloatField(default=0, null=True)
    formateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='formation_post')
    categorie = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    update_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return self.nom


# Table Devis - Demandes de devis des utilisateurs
class Devis(models.Model):
    """Modèle pour les demandes de devis des clients"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validé'),
        ('REFUSE', 'Refusé'),
        ('EN_COURS', 'En cours de traitement'),
        ('TERMINE', 'Terminé'),
    ]
    
    TYPE_PROJET_CHOICES = [
        ('DEVIS_GENERAL', 'Demande de devis générale'),
        ('SITE_WEB', 'Site Web'),
        ('APPLICATION', 'Application Mobile/Desktop'),
        ('LOGICIEL', 'Logiciel sur mesure'),
        ('RESEAU', 'Infrastructure Réseau'),
        ('SECURITE', 'Cyber Sécurité'),
        ('MARKETING', 'Marketing Digital'),
        ('FORMATION', 'Formation'),
        ('CONSULTING', 'Consulting IT'),
        ('MAINTENANCE', 'Maintenance/Support'),
        ('AUTRE', 'Autre'),
    ]
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devis'
    )
    titre = models.CharField(max_length=255, blank=True, null=True)
    type_projet = models.CharField(max_length=25, choices=TYPE_PROJET_CHOICES, default='AUTRE')
    description = models.TextField(help_text="Description détaillée du projet")
    budget_estime = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    date_souhaitee = models.DateField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    montant = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Montant proposé par l'admin")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    date_reponse = models.DateTimeField(blank=True, null=True)
    reponse_admin = models.TextField(blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
    
    def __str__(self):
        return f"Devis #{self.id} - {self.client.username} ({self.get_statut_display()})"
    
    def annuler(self):
        """Annuler la demande de devis"""
        self.statut = 'REFUSE'
        self.est_actif = False
        self.save()
    
    def valider(self, montant_propose=None):
        """Valider le devis avec un montant proposé"""
        self.statut = 'VALIDE'
        if montant_propose:
            self.montant = montant_propose
        self.date_reponse = timezone.now()
        self.save()

