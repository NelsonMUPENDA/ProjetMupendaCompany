from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, Apropos, Equipement, Services, Post, Category, Realisation, 
                    TemoignageClient, Formation, Contact, Formateur, Client, 
                    HistoriqueInteraction, AssociationClientProjet, Permission, Role, UserRole,
                    Departement, Projet, Tache, Notification, LogAction, 
                    AffectationCollaborateur, SuiviTemps,
                    Partenaire, FAQ, PageLegale, NewsletterSubscriber, NewsletterCampaign, Devis,
                    SiteContact)

admin.site.site_header = "mupenda.cd | Administration"
admin.site.site_title = "mupenda.cd"
admin.site.index_title = "mupenda.cd"

class ServicesAdmin (admin.ModelAdmin):
    list_display = ('id','nom', 'slug', 'description', 'photo', 'status', 'date_ajout', 'update_on')
    # list_filter = ('nom')
    search_fields = ['id', 'nom', 'description', 'status', 'date_ajout']
    prepopulated_fields = {'slug' : ('nom',)}

class AproposAdmin(admin.ModelAdmin):
    """Admin pour le modèle Apropos amélioré avec toutes les sections dynamiques"""
    
    list_display = (
        'id', 'nom_entreprise', 'titre_page', 'annee_experience', 
        'nombre_projets', 'nombre_clients', 'est_actif', 'date_modification'
    )
    list_filter = ('est_actif', 'date_modification', 'date_creation')
    search_fields = ('nom_entreprise', 'titre_page', 'sous_titre_page', 'description_entreprise')
    ordering = ['-date_modification']
    
    fieldsets = (
        ('Header', {
            'fields': ('titre_page', 'sous_titre_page'),
            'classes': ('wide',)
        }),
        ('Section Principale', {
            'fields': ('nom_entreprise', 'photo_principale', 'description_entreprise'),
            'classes': ('wide',)
        }),
        ('Statistiques', {
            'fields': (
                ('annee_experience', 'label_annee_experience'),
                ('nombre_projets', 'label_projets'),
                ('nombre_clients', 'label_clients'),
            ),
            'classes': ('wide',)
        }),
        ('Section Valeurs - Objectifs', {
            'fields': (
                'titre_objectifs', 'icon_objectifs',
                'objectif_1', 'objectif_2', 'objectif_3', 'objectif_4'
            ),
            'classes': ('collapse',)
        }),
        ('Section Valeurs - Valeurs', {
            'fields': (
                'titre_valeurs', 'icon_valeurs',
                'valeur_1', 'valeur_2', 'valeur_3', 'valeur_4'
            ),
            'classes': ('collapse',)
        }),
        ('Section Valeurs - Mission', {
            'fields': (
                'titre_mission', 'icon_mission',
                'mission_1', 'mission_2', 'mission_3', 'mission_4'
            ),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('titre_section_valeurs', 'est_actif'),
            'classes': ('wide',)
        }),
        ('Métadonnées', {
            'fields': ('auteur', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('date_creation', 'date_modification')
    
    def save_model(self, request, obj, form, change):
        """Sauvegarde avec l'auteur courant"""
        if not obj.auteur:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)

class RealisationAdmin (admin.ModelAdmin):
    list_display = ('id', 'titre', 'slug', 'description', 'image', 'auteur', 'category', 'status', 'created_on', 'update_on')
    search_fields = ['id','titre', 'description', 'category', 'created_on', 'status']
    prepopulated_fields = {'slug' : ('titre',)}

class TemoignageAdmin (admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'message', 'image', 'auteur', 'status', 'created_on', 'update_on')
    search_fields = ['id', 'nom', 'prenom', 'auteur', 'status', 'created_on']

class FormationAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'slug', 'description', 'image', 'date_debut', 'date_fin', 'heure_debut', 'heure_fin', 'prix', 'formateur', 'categorie', 'created_on', 'update_on', 'status')
    search_fields = ('id', 'nom', 'date_debut', 'date_fin', 'heure_debut', 'heure_fin', 'prix', 'formateur', 'categorie', 'status')
    prepopulated_fields = {'slug' : ('nom',)}

class CategoryAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'created_on', 'update_on')
    search_fields = ['name']

class PostAdmin (admin.ModelAdmin):
    list_display = ('id', 'titre', 'slug', 'author', 'content', 'categorie', 'image', 'status', 'created_on', 'update_on')
    list_filter = ('titre', 'created_on', 'author')
    search_fields = ['id', 'titre', 'content', 'author', 'categorie', 'status']
    date_hierarchy = ('created_on')
    # ordering = ('created_on')
    prepopulated_fields = {'slug': ('titre',)}
    
class SiteContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'adresse_complete', 'telephone_principal', 'email_principal', 'horaires_ouverture', 'est_actif', 'date_modification')
    list_filter = ('est_actif', 'date_creation')
    search_fields = ['adresse_complete', 'email_principal', 'telephone_principal']
    
    fieldsets = (
        ('Coordonnées', {
            'fields': ('telephone_principal', 'telephone_secondaire', 'email_principal', 'email_support')
        }),
        ('Adresse et Horaires', {
            'fields': ('adresse_complete', 'horaires_ouverture')
        }),
        ('Réseaux Sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Carte', {
            'fields': ('carte_embed_url',),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('est_actif',),
        }),
    )

class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'phone', 'email', 'message', 'created_on')
    search_fields = ['id', 'prenom', 'nom']
    # list_filter = ('')

class EquipementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'model', 'marque', 'color', 'quantity', 'image', 'author', 'autres_details', 'created_on','update_on')
    search_fields = ['id', 'name', 'model', 'marque', 'color']
    prepopulated_fields = {'slug': ('name',)}

class FormateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'postnom', 'prenom', 'sexe', 'age', 'email', 'phone', 'addresse', 'image', 'specialite', 'created_on', 'update_on')
    search_fields = ('id', 'nom', 'postnom', 'prenom', 'email', 'specialite')
    list_filter = ('nom', 'prenom')
    
class UserAdmin (admin.ModelAdmin):
    list_display = ('id', 'photo_profil', 'username', 'email', 'is_administrateur', 'is_utilisateur', 'is_staff')
    search_fields = ('id', 'username', 'email')
    list_filter = ('is_administrateur', 'is_utilisateur', 'is_staff')

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Apropos, AproposAdmin)
admin.site.register(Services, ServicesAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Realisation, RealisationAdmin)
admin.site.register(TemoignageClient, TemoignageAdmin)
admin.site.register(Formation, FormationAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Equipement, EquipementAdmin)
admin.site.register(Formateur, FormateurAdmin)

# Admin pour les modèles de gestion des clients
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'email', 'type_client', 'statut_client', 'responsable_compte', 'date_creation')
    list_filter = ('type_client', 'statut_client', 'date_creation')
    search_fields = ['nom', 'email', 'adresse']
    ordering = ['-date_creation']
    readonly_fields = ('date_creation', 'date_maj')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'email', 'telephone', 'adresse')
        }),
        ('Classification', {
            'fields': ('type_client', 'statut_client')
        }),
        ('Informations entreprise', {
            'fields': ('siret', 'secteur_activite', 'site_web'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('responsable_compte', 'notes')
        }),
        ('Timestamps', {
            'fields': ('date_creation', 'date_maj'),
            'classes': ('collapse',)
        })
    )

class HistoriqueInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'type_interaction', 'date_interaction', 'sujet', 'participant', 'duree_minutes')
    list_filter = ('type_interaction', 'date_interaction', 'participant')
    search_fields = ['client__nom', 'sujet', 'description']
    ordering = ['-date_interaction']
    date_hierarchy = 'date_interaction'
    readonly_fields = ('cree_le',)
    
    fieldsets = (
        ('Interaction', {
            'fields': ('client', 'type_interaction', 'date_interaction', 'sujet')
        }),
        ('Détails', {
            'fields': ('duree_minutes', 'description', 'participant', 'prochain_rappel')
        }),
        ('Timestamp', {
            'fields': ('cree_le',),
            'classes': ('collapse',)
        })
    )

class AssociationClientProjetAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'projet', 'role_dans_projet', 'statut_association', 'date_debut_association', 'budget_alloue')
    list_filter = ('statut_association', 'date_debut_association')
    search_fields = ['client__nom', 'projet__titre', 'role_dans_projet']
    ordering = ['-date_debut_association']
    readonly_fields = ('cree_le',)
    
    fieldsets = (
        ('Association', {
            'fields': ('client', 'projet', 'role_dans_projet')
        }),
        ('Informations projet', {
            'fields': ('budget_alloue', 'date_debut_association', 'date_fin_association', 'statut_association')
        }),
        ('Notes', {
            'fields': ('notes_association',)
        }),
        ('Timestamp', {
            'fields': ('cree_le',),
            'classes': ('collapse',)
        })
    )

# Enregistrement des modèles clients
admin.site.register(Client, ClientAdmin)
admin.site.register(HistoriqueInteraction, HistoriqueInteractionAdmin)
admin.site.register(AssociationClientProjet, AssociationClientProjetAdmin)

# ============================================================================
# ADMIN POUR LA GESTION DES RÔLES ET PERMISSIONS
# ============================================================================

class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'nom', 'categorie', 'est_active')
    list_filter = ('categorie', 'est_active')
    search_fields = ('code', 'nom', 'description')
    ordering = ['categorie', 'nom']

class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'get_nom_display', 'niveau_hierarchique', 'est_actif', 'date_creation')
    list_filter = ('est_actif', 'niveau_hierarchique')
    search_fields = ('nom', 'description')
    filter_horizontal = ('permissions',)
    ordering = ['-niveau_hierarchique', 'nom']

class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'role', 'est_actif', 'date_attribution', 'attribue_par')
    list_filter = ('role', 'est_actif', 'date_attribution')
    search_fields = ('utilisateur__username', 'utilisateur__email', 'role__nom')
    ordering = ['-date_attribution']
    autocomplete_fields = ['utilisateur', 'role', 'attribue_par']

# Enregistrement des modèles de gestion des rôles
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(UserRole, UserRoleAdmin)

# ============================================================================
# ADMIN POUR LA GESTION D'ENTREPRISE (PROJETS, DÉPARTEMENTS, TÂCHES)
# ============================================================================

class DepartementAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'responsable', 'couleur', 'est_actif', 'date_creation')
    list_filter = ('est_actif',)
    search_fields = ('nom', 'description')
    ordering = ['nom']
    autocomplete_fields = ['responsable']

class ProjetAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'statut', 'priorite', 'client', 'departement', 'chef_projet', 'date_debut', 'date_fin_prevue', 'progression')
    list_filter = ('statut', 'priorite', 'departement', 'date_debut')
    search_fields = ('nom', 'description', 'client')
    ordering = ['-date_debut']
    filter_horizontal = ('equipe',)
    autocomplete_fields = ['departement', 'chef_projet', 'cree_par']
    date_hierarchy = 'date_debut'

class TacheAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'projet', 'statut', 'priorite', 'assigne_a', 'date_echeance', 'temps_estime', 'temps_passe')
    list_filter = ('statut', 'priorite', 'projet')
    search_fields = ('titre', 'description')
    ordering = ['-date_creation']
    autocomplete_fields = ['projet', 'assigne_a', 'cree_par']
    date_hierarchy = 'date_echeance'

# Enregistrement des modèles de gestion d'entreprise
admin.site.register(Departement, DepartementAdmin)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Tache, TacheAdmin)

# ============================================================================
# ADMIN POUR NOTIFICATIONS, LOGS ET SUIVI
# ============================================================================

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'destinataire', 'type_notification', 'est_lue', 'date_creation')
    list_filter = ('type_notification', 'est_lue', 'date_creation')
    search_fields = ('titre', 'message', 'destinataire__username')
    ordering = ['-date_creation']
    autocomplete_fields = ['destinataire']
    date_hierarchy = 'date_creation'

class LogActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'action', 'modele', 'date_action', 'adresse_ip')
    list_filter = ('action', 'modele', 'date_action')
    search_fields = ('utilisateur__username', 'modele', 'description')
    ordering = ['-date_action']
    autocomplete_fields = ['utilisateur']
    date_hierarchy = 'date_action'
    readonly_fields = ('date_action',)

class AffectationCollaborateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'collaborateur', 'projet', 'role', 'date_affectation', 'est_actif')
    list_filter = ('role', 'est_actif', 'date_affectation')
    search_fields = ('collaborateur__username', 'projet__nom')
    ordering = ['-date_affectation']
    autocomplete_fields = ['collaborateur', 'projet']

class SuiviTempsAdmin(admin.ModelAdmin):
    list_display = ('id', 'collaborateur', 'projet', 'date_saisie', 'heures', 'type_travail', 'statut', 'montant')
    list_filter = ('statut', 'type_travail', 'date_saisie')
    search_fields = ('collaborateur__username', 'projet__nom', 'description')
    ordering = ['-date_saisie']
    autocomplete_fields = ['projet', 'collaborateur', 'valide_par']
    date_hierarchy = 'date_saisie'
    readonly_fields = ('cree_le', 'modifie_le')

# Enregistrement des modèles de notification, logs et suivi
admin.site.register(Notification, NotificationAdmin)
admin.site.register(LogAction, LogActionAdmin)
admin.site.register(AffectationCollaborateur, AffectationCollaborateurAdmin)
admin.site.register(SuiviTemps, SuiviTempsAdmin)

# ============================================================================
# ADMIN POUR LES MODÈLES MANQUANTS (Partenaire, FAQ, PageLegale, Newsletter, Devis)
# ============================================================================

class PartenaireAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'site_web', 'est_actif', 'ordre_affichage')
    list_filter = ('est_actif',)
    search_fields = ('nom', 'description')
    ordering = ['ordre_affichage', 'nom']

class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'categorie', 'est_active', 'ordre_affichage', 'created_on')
    list_filter = ('categorie', 'est_active')
    search_fields = ('question', 'reponse')
    ordering = ['categorie', 'ordre_affichage']

class PageLegaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_page', 'titre', 'est_active', 'derniere_mise_a_jour')
    list_filter = ('type_page', 'est_active')
    search_fields = ('titre', 'contenu')

class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nom', 'prenom', 'est_actif', 'date_inscription')
    list_filter = ('est_actif', 'date_inscription')
    search_fields = ('email', 'nom', 'prenom')
    ordering = ['-date_inscription']

class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ('id', 'sujet', 'date_envoi', 'envoye_par', 'nombre_destinataires', 'nombre_ouverts', 'est_brouillon')
    list_filter = ('est_brouillon', 'date_envoi')
    search_fields = ('sujet', 'contenu')
    ordering = ['-date_envoi']

class DevisAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'titre', 'type_projet', 'statut', 'montant', 'date_creation')
    list_filter = ('statut', 'type_projet', 'date_creation')
    search_fields = ('client__username', 'titre', 'description')
    ordering = ['-date_creation']
    autocomplete_fields = ['client']

# Enregistrement des modèles manquants
admin.site.register(Partenaire, PartenaireAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(PageLegale, PageLegaleAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
admin.site.register(NewsletterCampaign, NewsletterCampaignAdmin)
admin.site.register(Devis, DevisAdmin)
admin.site.register(SiteContact, SiteContactAdmin)
