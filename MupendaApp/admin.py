from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Apropos, Equipement, Services, Post, Category, Realisation, TemoignageClient, Formation, Contact, Formateur, Client, HistoriqueInteraction, AssociationClientProjet

admin.site.site_header = "mupenda.cd | Administration"
admin.site.site_title = "mupenda.cd"
admin.site.index_title = "mupenda.cd"

class ServicesAdmin (admin.ModelAdmin):
    list_display = ('id','nom', 'slug', 'description', 'photo', 'status', 'date_ajout', 'update_on')
    # list_filter = ('nom')
    search_fields = ['id', 'nom', 'description', 'status', 'date_ajout']
    prepopulated_fields = {'slug' : ('nom',)}

class AproposAdmin (admin.ModelAdmin):
    list_display = ('id', 'nom', 'contenus', 'photo', 'auteur', 'date_ajout', 'update_on')

class RealisationAdmin (admin.ModelAdmin):
    list_display = ('id', 'titre', 'slug', 'description', 'image', 'auteur', 'category', 'status', 'created_on', 'update_on')
    search_fields = ['id','titre', 'description', 'category', 'created_on', 'status']
    prepopulated_fields = {'slug' : ('titre',)}

class TemoignageAdmin (admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'message', 'image', 'auteur', 'status', 'created_on', 'update_on')
    search_fields = ['id', 'nom', 'prenom', 'auteur', 'status', 'created_on']

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
    
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'phone', 'email', 'message', 'created_on')
    search_fields = ['id', 'prenom', 'nom']
    # list_filter = ('')

class EquipementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'model', 'marque', 'color', 'quantity', 'image', 'author', 'autres_details', 'created_on','update_on')
    search_fields = ['id', 'name', 'model', 'marque', 'color']
    prepopulated_fields = {'slug': ('name',)}

class FormationAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'slug', 'description', 'image', 'date_debut', 'date_fin', 'heure_debut', 'heure_fin', 'prix', 'formateur', 'categorie', 'created_on', 'update_on', 'status')
    search_fields = ('id', 'nom', 'date_debut', 'date_fin', 'heure_debut', 'heure_fin', 'prix', 'formateur', 'categorie', 'status')
    prepopulated_fields = {'slug' : ('nom',)}

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
