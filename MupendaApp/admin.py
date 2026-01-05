from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Apropos, Equipement, Services, Post, Category, Realisation, TemoignageClient, Formation, Contact, Formateur

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
