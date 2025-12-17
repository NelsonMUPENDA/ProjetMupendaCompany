from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from .models import Services, Apropos, Realisation, Post, Contact, Formation
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views import generic
from MupendaApp.forms import UserForm, InsertApropos, FormationForm
import os


# Create your views here.
class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by ('-created_on')
    template_name = 'blog.html'

class BlogDetailView(generic.DetailView):
    model = Post
    template_name = 'blog_detail.html'

class FormationList(generic.ListView):
    queryset = Formation.objects.filter(status=1).order_by ('-date_debut')
    template_name = 'formation.html'

class FormationDetailView(generic.DetailView):
    model = Formation
    template_name = 'detail_formation.html'

def index(request):
    service = Services.objects.all()
    afficher = Realisation.objects.all()
    afficherApropos = Apropos.objects.all()
    return render(
        request, 'index.html', 
        context={
            "service":service, 
            "afficher":afficher, 
            'afficherApropos':afficherApropos,
            }
        )

#Inscription
User = get_user_model()

def inscription(request):
    form = UserForm()
    if request.method == "POST":
        form = UserForm(data=request.POST)
        if form.is_valid():
            form.save
            return redirect('connexion.html')
    return render(request, 'inscription.html', {'form':form})
    
# Connexion 

def connexion(request):
    erreur = ''
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login (request, user)

            if user.is_administrateur:
                return redirect('administration/indexAdmin')
            else:
                return redirect('profil')
        else:
            erreur = 'Votre nom d\'utilisateur ou mot de passe est incorrecte' 
    return render(request, 'connexion.html', {'erreur':erreur})

# Fin connexion 

def indexAdmin(request):
    return render(request, 'administration/indexAdmin.html')

def dashboard(request):
    return render(request, 'administration/dashboard.html')

def profil(request):
    return render(request, 'profil.html')

def deconnexion(request):
    logout(request)
    return redirect('connexion')

# Cette fonction permet Ajouter dans la BD
def contact(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        phone = request.POST['phone']
        email = request.POST['email']
        message = request.POST['message']
        
        form = Contact(nom=nom, prenom=prenom, phone=phone, email=email, message=message)
        form.save()
        
    return render(request, 'contact.html')

def apropos(request):
    apropos = Apropos.objects.all()
    return render(request, 'apropos.html', context={"apropos":apropos})

def blog(request):
    return render(request, 'blog.html')

def realisations(request):
    afficher = Realisation.objects.all()
    return render(request, 'realisations.html', context={"afficher":afficher})

def cgu(request):
    return render(request, 'conditionUtilisation.html')

def politique(request):
    return render(request, "politique.html")

def faq(request):
    return render(request, "faq.html")

def formation(request):
    return render(request, "formation.html")

# PARTIE ADMINISTRATIVE

# Cette fonction permet d'ajouter les données dans la BD
def AdminApropos(request):
    if request.method == 'POST':
        form = InsertApropos(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = InsertApropos()
        afficher = Apropos.objects.all()
    return render(request, 'administration/apropos.html', {'form':form, 'afficher':afficher})

# Cette fonction permet de modifier les données de la table Apropos
def UpdateApropos(request, id):
    x = Apropos.objects.get(pk=id)
    form = UpdateApropos(request.POST, instance=x)
    if form.is_valid():
        form.save()
    else:
        x = Apropos.objects.get(pk=id)
        form = UpdateApropos(instance=x)
    return render(request, 'administration/updateApropos.html', {'form':form})

def AdminTemoignage(request):
    return render(request, 'administration/temoignage.html')

# ==============================================================================

# Cette fonction permet d'inserer ET D'AFFICHER      
def AdminService(request):
    if request.method == 'POST':
        form = Services()
        form.nom = request.POST.get('nom')
        form.description = request.POST.get('description')

        if len(request.FILES) != 0:
            form.photo = request.FILES['image']
            form.save()
            messages.success(request, "Service enregistré avec succès !")
            return redirect('/service.html')
        
    afficherService = Services.objects.all()
    return render(request, 'administration/service.html', {'afficherService':afficherService})


def AdminRealisation(request):
    if request.method == 'POST':
        form = Realisation()
        form.titre = request.POST.get('nom')
        form.description = request.POST.get('description')

        if len(request.FILES) != 0:
            form.image = request.FILES['image']
            form.save()
            messages.success(request, "Enregistrement effectué avec succès !")
            return redirect('AdminRealisation')
    afficherRealisation = Realisation.objects.all()
    return render(request, 'administration/realisation.html', {'afficherRealisation':afficherRealisation})

def AdminContact(request):
    afficherMessage = Contact.objects.all()
    return render(request, 'administration/contact.html', {'afficherMessage':afficherMessage})


# Cette fonction permet de modifier

def EditService(request, pk):
    edit = Services.objects.get(id=pk)

    if request.method == 'POST':
        if len(request.FILES) != 0:
            if len(edit.photo) > 0:
                os.remove(edit.photo.path)
            edit.photo = request.FILES['image']
        edit.nom = request.POST.get('nom')
        edit.description = request.POST.get('description')
        edit.save()
        messages.success(request, "Service modifié avec succès ! ")
        return redirect('AdminService')

    return render(request, 'administration/edit_service.html', {'edit':edit},)

def EditRealisation(request, pk):
    edit_real = Realisation.objects.get(id=pk)

    if request.method == 'POST':
        if len(request.FILES) != 0:
            if len(edit_real.image) > 0:
                os.remove(edit_real.image.path)
            edit_real.image = request.FILES['image']
            edit_real.titre = request.POST.get('nom')
            edit_real.description = request.POST.get('description')
            edit_real.save()
            messages.success(request, "Les modifications sont appliquées avec succès !")
            return redirect('AdminRealisation')
        
    return render(request, 'administration/edit_realisation.html', {'edit_real':edit_real},)

# Cette fonction permet de supprimer

def DeleteService(request, pk):
    delete_service = Services.objects.get(id=pk)
    if len(delete_service.photo) > 0:
        os.remove(delete_service.photo.path)
    delete_service.delete()
    messages.success(request, "Service supprimé avec succès !")
    return redirect('AdminService')

def DeleteRealisation(request, pk):
    delete_realisation = Realisation.objects.get(id=pk)
    if len(delete_realisation.image) > 0:
        os.remove(delete_realisation.image.path)
    delete_realisation.delete()
    messages.success(request, "Suppresion effecutée avec succès !")
    return redirect('AdminRealisation')
# =================================================================================

def AdminPartenaire(request):
    return render(request, 'administration/partenaire.html')

def AdminFormation(request):
    form = FormationForm()
    if request.method == "POST":
        form = FormationForm(data=request.POST)
        if form.is_valid():
            form.save
            return redirect('AdminFormation')
    return render(request, 'administration/formation.html', {'form':form})

def AdminBlog(request):
    return render(request, 'administration/blog.html')

def AdminFaq(request):
    return render(request, 'administration/faq.html')


