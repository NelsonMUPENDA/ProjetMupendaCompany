import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from ckeditor.fields import RichTextField

STATUS = ((0,"Draft "), (1,"Publié "))

#Table Categorie

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    update_on = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    is_administrateur = models.BooleanField(default=False)
    is_utilisateur = models.BooleanField(default=True)

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
    description = RichTextField(null=True)
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
    update_on = models.DateTimeField(auto_now_add=True, null=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return self.nom

#Table Apropos

class Apropos(models.Model):
    nom = models.CharField(max_length=255, unique=True, null=True)
    contenus = RichTextField(null=True)
    photo = models.ImageField(upload_to="static/images", blank=True, null=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='apropos',
        null=True
    )
    date_ajout = models.DateTimeField(auto_now=True)
    update_on = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['date_ajout']

    def __str__(self):
        return self.nom

#Table Services

class Services(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    description = RichTextField(null=True)
    photo = models.ImageField(upload_to="static/images", blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now_add=True, null=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['date_ajout']

    def __str__(self):
        return self.nom

#Table Realisation

class Realisation(models.Model):
    titre = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    description = RichTextField(null=True)
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
    update_on = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.titre
    
# Table Temoignage

class TemoignageClient(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, null=True)
    message = RichTextField(null=True)
    image = models.ImageField(upload_to="static/images", blank=True, null=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='temoignage_client',
        null=True
    )
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    update_on = models.DateTimeField(auto_now_add=True, null=True)
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
    content = RichTextField()
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
    update_on = models.DateTimeField(auto_now_add=True)

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
    update_on = models.DateField(auto_now_add=True)

# Table 
