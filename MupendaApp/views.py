from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.views import generic
from .models import (
    Client, Projet, SuiviTemps, AffectationCollaborateur, 
    Devis, Facture, LigneFacture, Collaborateur, TicketSupport, MessageTicket,
    Services, Apropos, Realisation, Post, Contact, Formation, TemoignageClient, Category
)
from .forms import (
    FormationForm, UserForm, InsertApropos
)
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
    return render(request, 'index.html', {'afficherApropos': afficherApropos, 'service':service, 'afficher':afficher})

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

            if user.is_superuser:
                return redirect('dashboard')
            else:
                return redirect('profil')
        else:
            erreur = 'Votre nom d\'utilisateur ou mot de passe est incorrecte' 
    return render(request, 'connexion.html', {'erreur':erreur})

# Fin connexion 

def indexAdmin(request):
    return render(request, 'administration/indexAdmin.html')

def dashboard(request):
    count_services = Services.objects.count()
    count_realisations = Realisation.objects.count()
    count_formations = Formation.objects.count()
    count_contacts = Contact.objects.count()
    count_temoignages = TemoignageClient.objects.count()
    count_blogs = Post.objects.count()
    count_categories = Category.objects.count()
    
    context = {
        'count_services': count_services,
        'count_realisations': count_realisations,
        'count_formations': count_formations,
        'count_contacts': count_contacts,
        'count_temoignages': count_temoignages,
        'count_blogs': count_blogs,
        'count_categories': count_categories,
    }
    return render(request, 'administration/dashboard.html', context)

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

def service(request):
    service = Services.objects.all()
    return render(request, 'services.html', context={"service":service})

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
def UpdateApropos(request, id_apropos):
    edit_apropos = Apropos.objects.get(id=id_apropos)
    if request.method == 'POST':
        edit_apropos.nom = request.POST.get('nom')
        edit_apropos.contenus = request.POST.get('contenus')
        edit_apropos.save()
        messages.success(request, "Modification effectuée avec succès !")
        return redirect('AdminApropos')
    else:
        messages.error(request, "Erreur lors de la modification !")
    return render(request, 'administration/updateApropos.html', {'edit_apropos':edit_apropos})

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
        messages.success(request, "Modification effectuée avec succès !")
        return redirect('AdminService')
    return render(request, 'administration/edit_service.html', {'edit':edit})

def DeleteService(request, pk):
    delete = Services.objects.get(id=pk)
    delete.delete()
    messages.success(request, "Suppression effectuée avec succès !")
    return redirect('AdminService')

def EditRealisation(request, pk):
    edit = Realisation.objects.get(id=pk)

    if request.method == 'POST':
        if len(request.FILES) != 0:
            if len(edit.image) > 0:
                os.remove(edit.image.path)
            edit.image = request.FILES['image']
        edit.titre = request.POST.get('nom')
        edit.description = request.POST.get('description')
        edit.save()
        messages.success(request, "Modification effectuée avec succès !")
        return redirect('AdminRealisation')
    return render(request, 'administration/edit_realisation.html', {'edit':edit})

def DeleteRealisation(request, pk):
    delete = Realisation.objects.get(id=pk)
    delete.delete()
    messages.success(request, "Suppression effectuée avec succès !")
    return redirect('AdminRealisation')

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

# FACTURATION
@login_required
def FacturationView(request):
    """Vue principale pour la facturation"""
    # Statistiques
    stats = {
        'total_devis': Devis.objects.count(),
        'devis_en_attente': Devis.objects.filter(statut='BROUILLON').count(),
        'total_factures': Facture.objects.count(),
        'factures_impayees': Facture.objects.filter(statut='ENVOYEE').count(),
        'chiffre_affaires': Facture.objects.filter(statut='PAYEE').aggregate(total=Sum('montant_ttc'))['total'] or 0,
        'factures_en_retard': Facture.objects.filter(statut='EN_RETARD').count(),
    }
    
    # Devis récents
    devis_recents = Devis.objects.select_related('client', 'projet').order_by('-date_emission')[:5]
    
    # Factures récentes
    factures_recentes = Facture.objects.select_related('client', 'projet').order_by('-date_emission')[:5]
    
    return render(request, 'administration/facturation/index_facturation.html', {
        'stats': stats,
        'devis_recents': devis_recents,
        'factures_recentes': factures_recentes,
    })

@login_required
def ListeDevisView(request):
    """Vue pour la liste des devis"""
    search = request.GET.get('search', '')
    statut_filter = request.GET.get('statut', '')
    client_filter = request.GET.get('client', '')
    
    devis = Devis.objects.select_related('client', 'projet', 'cree_par')
    
    if search:
        devis = devis.filter(
            Q(numero__icontains=search) |
            Q(client__nom__icontains=search) |
            Q(projet__nom__icontains=search)
        )
    
    if statut_filter:
        devis = devis.filter(statut=statut_filter)
    
    if client_filter:
        devis = devis.filter(client_id=client_filter)
    
    return render(request, 'administration/facturation/liste_devis.html', {
        'devis': devis.order_by('-date_emission'),
        'statut_choices': Devis.STATUT_CHOICES,
        'clients': Client.objects.all(),
        'search': search,
        'statut_filter': statut_filter,
        'client_filter': client_filter,
    })

@login_required
def AjouterDevisView(request):
    """Vue pour ajouter un devis"""
    if request.method == 'POST':
        try:
            devis = Devis(
                numero=Devis().generer_numero(),
                client_id=request.POST.get('client'),
                projet_id=request.POST.get('projet') or None,
                date_validite=request.POST.get('date_validite'),
                montant_ht=request.POST.get('montant_ht'),
                montant_tva=request.POST.get('montant_tva', 0),
                notes=request.POST.get('notes', ''),
                conditions_paiement=request.POST.get('conditions_paiement', 'Paiement à 30 jours'),
                cree_par=request.user,
            )
            devis.save()
            messages.success(request, f"Devis {devis.numero} créé avec succès!")
            return redirect('fiche_devis', devis_id=devis.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/facturation/ajouter_devis.html', {
        'clients': Client.objects.all(),
        'projets': Projet.objects.all(),
    })

@login_required
def FicheDevisView(request, devis_id):
    """Vue pour la fiche détaillée d'un devis"""
    devis = get_object_or_404(Devis, id=devis_id)
    
    # Vérifier si le devis peut être converti en facture
    peut_convertir = devis.statut == 'ACCEPTE' and not hasattr(devis, 'facture')
    
    return render(request, 'administration/facturation/fiche_devis.html', {
        'devis': devis,
        'peut_convertir': peut_convertir,
    })

@login_required
def ConvertirDevisFactureView(request, devis_id):
    """Vue pour convertir un devis en facture"""
    devis = get_object_or_404(Devis, id=devis_id)
    
    if devis.statut != 'ACCEPTE':
        messages.error(request, "Seuls les devis acceptés peuvent être convertis en factures")
        return redirect('fiche_devis', devis_id=devis_id)
    
    if hasattr(devis, 'facture'):
        messages.error(request, "Ce devis a déjà été converti en facture")
        return redirect('fiche_devis', devis_id=devis_id)
    
    try:
        facture = Facture(
            numero=Facture().generer_numero(),
            devis=devis,
            client=devis.client,
            projet=devis.projet,
            montant_ht=devis.montant_ht,
            montant_tva=devis.montant_tva,
            notes=devis.notes,
            cree_par=request.user,
        )
        facture.save()
        
        messages.success(request, f"Facture {facture.numero} créée à partir du devis {devis.numero}")
        return redirect('fiche_facture', facture_id=facture.id)
    except Exception as e:
        messages.error(request, f"Erreur lors de la conversion: {str(e)}")
        return redirect('fiche_devis', devis_id=devis_id)

@login_required
def ListeFacturesView(request):
    """Vue pour la liste des factures"""
    search = request.GET.get('search', '')
    statut_filter = request.GET.get('statut', '')
    client_filter = request.GET.get('client', '')
    periode = request.GET.get('periode', '')
    
    factures = Facture.objects.select_related('client', 'projet', 'cree_par')
    
    if search:
        factures = factures.filter(
            Q(numero__icontains=search) |
            Q(client__nom__icontains=search) |
            Q(projet__nom__icontains=search)
        )
    
    if statut_filter:
        factures = factures.filter(statut=statut_filter)
    
    if client_filter:
        factures = factures.filter(client_id=client_filter)
    
    if periode:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        if periode == 'mois':
            debut = today.replace(day=1)
            fin = (debut + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif periode == 'trimestre':
            mois = today.month
            if mois <= 3:
                debut = datetime(today.year, 1, 1).date()
                fin = datetime(today.year, 3, 31).date()
            elif mois <= 6:
                debut = datetime(today.year, 4, 1).date()
                fin = datetime(today.year, 6, 30).date()
            elif mois <= 9:
                debut = datetime(today.year, 7, 1).date()
                fin = datetime(today.year, 9, 30).date()
            else:
                debut = datetime(today.year, 10, 1).date()
                fin = datetime(today.year, 12, 31).date()
        else:  # année
            debut = datetime(today.year, 1, 1).date()
            fin = datetime(today.year, 12, 31).date()
        
        factures = factures.filter(date_emission__range=[debut, fin])
    
    return render(request, 'administration/facturation/liste_factures.html', {
        'factures': factures.order_by('-date_emission'),
        'statut_choices': Facture.STATUT_CHOICES,
        'clients': Client.objects.all(),
        'search': search,
        'statut_filter': statut_filter,
        'client_filter': client_filter,
        'periode': periode,
    })

@login_required
def FicheFactureView(request, facture_id):
    """Vue pour la fiche détaillée d'une facture"""
    facture = get_object_or_404(Facture, id=facture_id)
    lignes = facture.lignes.all()
    
    return render(request, 'administration/facturation/fiche_facture.html', {
        'facture': facture,
        'lignes': lignes,
    })

@login_required
def ExportPDFView(request, facture_id):
    """Vue pour exporter une facture en PDF (MVP - simple redirection)"""
    facture = get_object_or_404(Facture, id=facture_id)
    messages.info(request, f"Fonction PDF à implémenter pour la facture {facture.numero}")
    return redirect('fiche_facture', facture_id=facture_id)

# COLLABORATEURS
@login_required
def ListeCollaborateursView(request):
    """Vue pour la liste des collaborateurs"""
    search = request.GET.get('search', '')
    poste_filter = request.GET.get('poste', '')
    dispo_filter = request.GET.get('disponibilite', '')
    
    collaborateurs = Collaborateur.objects.select_related('user').filter(actif=True)
    
    if search:
        collaborateurs = collaborateurs.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(competences__icontains=search)
        )
    
    if poste_filter:
        collaborateurs = collaborateurs.filter(poste=poste_filter)
    
    if dispo_filter:
        collaborateurs = collaborateurs.filter(disponibilite=dispo_filter)
    
    return render(request, 'administration/collaborateurs/liste_collaborateurs.html', {
        'collaborateurs': collaborateurs.order_by('user__first_name'),
        'poste_choices': Collaborateur.POSTE_CHOICES,
        'dispo_choices': Collaborateur.DISPO_CHOICES,
        'search': search,
        'poste_filter': poste_filter,
        'dispo_filter': dispo_filter,
    })

@login_required
def AjouterCollaborateurView(request):
    """Vue pour ajouter un collaborateur"""
    if request.method == 'POST':
        try:
            # Créer ou récupérer l'utilisateur
            user = User.objects.get(username=request.POST.get('username'))
            
            collaborateur = Collaborateur(
                user=user,
                poste=request.POST.get('poste'),
                tjm=request.POST.get('tjm'),
                cout_horaire=request.POST.get('cout_horaire'),
                disponibilite=request.POST.get('disponibilite', 'DISPONIBLE'),
                competences=request.POST.get('competences'),
                date_embauche=request.POST.get('date_embauche'),
                telephone=request.POST.get('telephone', ''),
                linkedin=request.POST.get('linkedin', ''),
            )
            collaborateur.save()
            messages.success(request, f"Collaborateur {collaborateur} ajouté avec succès!")
            return redirect('fiche_collaborateur', collaborateur_id=collaborateur.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/collaborateurs/ajouter_collaborateur.html', {
        'poste_choices': Collaborateur.POSTE_CHOICES,
        'dispo_choices': Collaborateur.DISPO_CHOICES,
        'users': User.objects.all(),
    })

@login_required
def FicheCollaborateurView(request, collaborateur_id):
    """Vue pour la fiche détaillée d'un collaborateur"""
    collaborateur = get_object_or_404(Collaborateur, id=collaborateur_id)
    
    # Projets actifs
    projets_actifs = collaborateur.user.affectations.filter(est_actif=True).select_related('projet')
    
    # Temps saisi récent
    temps_recent = collaborateur.user.temps_saisi.order_by('-date_saisie')[:10]
    
    # Statistiques
    stats = {
        'total_projets': collaborateur.user.affectations.count(),
        'projets_actifs': projets_actifs.count(),
        'total_heures': collaborateur.user.temps_saisi.aggregate(total=Sum('heures'))['total'] or 0,
        'montant_total': collaborateur.user.temps_saisi.aggregate(total=Sum('montant'))['total'] or 0,
    }
    
    return render(request, 'administration/collaborateurs/fiche_collaborateur.html', {
        'collaborateur': collaborateur,
        'projets_actifs': projets_actifs,
        'temps_recent': temps_recent,
        'stats': stats,
    })

@login_required
def ModifierCollaborateurView(request, collaborateur_id):
    """Vue pour modifier un collaborateur"""
    collaborateur = get_object_or_404(Collaborateur, id=collaborateur_id)
    
    if request.method == 'POST':
        try:
            collaborateur.poste = request.POST.get('poste')
            collaborateur.tjm = request.POST.get('tjm')
            collaborateur.cout_horaire = request.POST.get('cout_horaire')
            collaborateur.disponibilite = request.POST.get('disponibilite')
            collaborateur.competences = request.POST.get('competences')
            collaborateur.telephone = request.POST.get('telephone', '')
            collaborateur.linkedin = request.POST.get('linkedin', '')
            collaborateur.actif = 'actif' in request.POST
            collaborateur.save()
            
            messages.success(request, f"Collaborateur {collaborateur} modifié avec succès!")
            return redirect('fiche_collaborateur', collaborateur_id=collaborateur.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/collaborateurs/modifier_collaborateur.html', {
        'collaborateur': collaborateur,
        'poste_choices': Collaborateur.POSTE_CHOICES,
        'dispo_choices': Collaborateur.DISPO_CHOICES,
    })

# SUPPORT CLIENT
@login_required
def SupportView(request):
    """Vue principale pour le support client"""
    # Statistiques
    stats = {
        'total_tickets': TicketSupport.objects.count(),
        'tickets_ouverts': TicketSupport.objects.filter(statut='OUVERT').count(),
        'tickets_en_cours': TicketSupport.objects.filter(statut='EN_COURS').count(),
        'tickets_resolus': TicketSupport.objects.filter(statut='RESOLU').count(),
        'tickets_urgents': TicketSupport.objects.filter(priorite='URGENTE').count(),
    }
    
    # Tickets récents
    tickets_recents = TicketSupport.objects.select_related('client', 'assigne_a').order_by('-date_creation')[:5]
    
    return render(request, 'administration/support/index_support.html', {
        'stats': stats,
        'tickets_recents': tickets_recents,
    })

@login_required
def ListeTicketsView(request):
    """Vue pour la liste des tickets"""
    search = request.GET.get('search', '')
    statut_filter = request.GET.get('statut', '')
    priorite_filter = request.GET.get('priorite', '')
    client_filter = request.GET.get('client', '')
    
    tickets = TicketSupport.objects.select_related('client', 'assigne_a', 'projet_concerne')
    
    if search:
        tickets = tickets.filter(
            Q(numero__icontains=search) |
            Q(titre__icontains=search) |
            Q(client__nom__icontains=search)
        )
    
    if statut_filter:
        tickets = tickets.filter(statut=statut_filter)
    
    if priorite_filter:
        tickets = tickets.filter(priorite=priorite_filter)
    
    if client_filter:
        tickets = tickets.filter(client_id=client_filter)
    
    return render(request, 'administration/support/liste_tickets.html', {
        'tickets': tickets.order_by('-date_creation'),
        'statut_choices': TicketSupport.STATUT_CHOICES,
        'priorite_choices': TicketSupport.PRIORITE_CHOICES,
        'clients': Client.objects.all(),
        'search': search,
        'statut_filter': statut_filter,
        'priorite_filter': priorite_filter,
        'client_filter': client_filter,
    })

@login_required
def AjouterTicketView(request):
    """Vue pour ajouter un ticket"""
    if request.method == 'POST':
        try:
            ticket = TicketSupport(
                client_id=request.POST.get('client'),
                titre=request.POST.get('titre'),
                description=request.POST.get('description'),
                type_demande=request.POST.get('type_demande', 'TECHNIQUE'),
                priorite=request.POST.get('priorite', 'NORMALE'),
                projet_concerne_id=request.POST.get('projet') or None,
                cree_par=request.user,
            )
            ticket.save()
            messages.success(request, f"Ticket {ticket.numero} créé avec succès!")
            return redirect('fiche_ticket', ticket_id=ticket.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/support/ajouter_ticket.html', {
        'type_choices': TicketSupport.TYPE_CHOICES,
        'priorite_choices': TicketSupport.PRIORITE_CHOICES,
        'clients': Client.objects.all(),
        'projets': Projet.objects.all(),
    })

@login_required
def FicheTicketView(request, ticket_id):
    """Vue pour la fiche détaillée d'un ticket"""
    ticket = get_object_or_404(TicketSupport, id=ticket_id)
    messages = ticket.messages.select_related('auteur').order_by('date_message')
    
    return render(request, 'administration/support/fiche_ticket.html', {
        'ticket': ticket,
        'messages': messages,
    })

@login_required
def AssignerTicketView(request, ticket_id):
    """Vue pour assigner un ticket"""
    ticket = get_object_or_404(TicketSupport, id=ticket_id)
    
    if request.method == 'POST':
        try:
            ticket.assigne_a_id = request.POST.get('assigne_a')
            ticket.statut = 'EN_COURS'
            ticket.save()
            
            # Ajouter un message système
            MessageTicket.objects.create(
                ticket=ticket,
                auteur=request.user,
                contenu=f"Ticket assigné à {ticket.assigne_a.get_full_name() or ticket.assigne_a.username}",
                est_interne=True
            )
            
            messages.success(request, f"Ticket {ticket.numero} assigné avec succès!")
            return redirect('fiche_ticket', ticket_id=ticket.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/support/assigner_ticket.html', {
        'ticket': ticket,
        'collaborateurs': User.objects.all(),
    })

@login_required
def ResoudreTicketView(request, ticket_id):
    """Vue pour résoudre un ticket"""
    ticket = get_object_or_404(TicketSupport, id=ticket_id)
    
    if request.method == 'POST':
        try:
            ticket.statut = 'RESOLU'
            ticket.resolu_par = request.user
            ticket.save()
            
            # Ajouter un message de résolution
            MessageTicket.objects.create(
                ticket=ticket,
                auteur=request.user,
                contenu="Ticket marqué comme résolu",
                est_interne=True
            )
            
            messages.success(request, f"Ticket {ticket.numero} résolu avec succès!")
            return redirect('fiche_ticket', ticket_id=ticket.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/support/resoudre_ticket.html', {
        'ticket': ticket,
    })

@login_required
def AjouterMessageView(request, ticket_id):
    """Vue pour ajouter un message à un ticket"""
    ticket = get_object_or_404(TicketSupport, id=ticket_id)
    
    if request.method == 'POST':
        try:
            message = MessageTicket.objects.create(
                ticket=ticket,
                auteur=request.user,
                contenu=request.POST.get('contenu'),
                est_interne='est_interne' in request.POST
            )
            
            # Si le ticket était en statut OUVERT, le passer en EN_COURS
            if ticket.statut == 'OUVERT':
                ticket.statut = 'EN_COURS'
                ticket.save()
            
            messages.success(request, "Message ajouté avec succès!")
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return redirect('fiche_ticket', ticket_id=ticket_id)

# VUES MANQUANTES POUR LES URLS EXISTANTES
@login_required
def AdministrationView(request):
    """Vue principale de l'administration"""
    return render(request, 'administration/indexAdmin.html')

@login_required
def TempsView(request):
    """Vue pour la gestion du temps"""
    return render(request, 'administration/suivi_temps.html')

@login_required
def ClientsView(request):
    """Vue pour la liste des clients"""
    search = request.GET.get('search', '')
    statut_filter = request.GET.get('statut_client', '')
    type_filter = request.GET.get('type_client', '')
    
    clients = Client.objects.all().order_by('nom')
    
    if search:
        clients = clients.filter(
            Q(nom__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )
    
    if statut_filter:
        clients = clients.filter(statut_client=statut_filter)
    
    if type_filter:
        clients = clients.filter(type_client=type_filter)
    
    return render(request, 'administration/liste_clients.html', {
        'clients': clients,
        'search': search,
        'statut_filter': statut_filter,
        'type_filter': type_filter,
        'statut_choices': Client.STATUT_CLIENT_CHOICES,
        'type_choices': Client.TYPE_CLIENT_CHOICES,
    })

@login_required
def AjouterClientView(request):
    """Vue pour ajouter un client"""
    if request.method == 'POST':
        try:
            client = Client(
                nom=request.POST.get('nom'),
                email=request.POST.get('email'),
                telephone=request.POST.get('telephone'),
                adresse=request.POST.get('adresse', ''),
                code_postal=request.POST.get('code_postal', ''),
                ville=request.POST.get('ville', ''),
                pays=request.POST.get('pays', 'Congo'),
                site_web=request.POST.get('site_web', ''),
                secteur_activite=request.POST.get('secteur_activite', ''),
                notes=request.POST.get('notes', ''),
            )
            client.save()
            messages.success(request, f"Client {client.nom} ajouté avec succès!")
            return redirect('clients')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/ajouter_client.html')

@login_required
def FicheClientView(request, client_id):
    """Vue pour la fiche détaillée d'un client"""
    client = get_object_or_404(Client, id=client_id)
    
    # Projets associés
    projets = client.projets.select_related('chef_projet').prefetch_related('affectations').order_by('-cree_le')
    
    # Devis associés
    devis = Devis.objects.filter(client=client).order_by('-date_emission')
    
    # Factures associées
    factures = Facture.objects.filter(client=client).order_by('-date_emission')
    
    # Tickets support
    tickets = TicketSupport.objects.filter(client=client).order_by('-date_creation')
    
    # Statistiques
    stats = {
        'total_projets': projets.count(),
        'projets_actifs': projets.filter(statut='EN_COURS').count(),
        'total_devis': devis.count(),
        'total_factures': factures.count(),
        'factures_impayees': factures.filter(statut='ENVOYEE').count(),
        'total_tickets': tickets.count(),
        'tickets_ouverts': tickets.filter(statut='OUVERT').count(),
        'chiffre_affaires': factures.filter(statut='PAYEE').aggregate(total=Sum('montant_ttc'))['total'] or 0,
    }
    
    return render(request, 'administration/fiche_client.html', {
        'client': client,
        'projets': projets,
        'devis': devis,
        'factures': factures,
        'tickets': tickets,
        'stats': stats,
    })

@login_required
def ModifierClientView(request, client_id):
    """Vue pour modifier un client"""
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        try:
            client.nom = request.POST.get('nom')
            client.adresse = request.POST.get('adresse')
            client.email = request.POST.get('email')
            client.telephone = request.POST.get('telephone')
            client.type_client = request.POST.get('type_client', 'PARTICULIER')
            client.statut_client = request.POST.get('statut_client', 'PROSPECT')
            client.siret = request.POST.get('siret', '')
            client.secteur_activite = request.POST.get('secteur_activite', '')
            client.site_web = request.POST.get('site_web', '')
            client.notes = request.POST.get('notes', '')
            
            # Gérer le responsable de compte
            responsable_id = request.POST.get('responsable_compte')
            if responsable_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    responsable = User.objects.get(id=responsable_id)
                    client.responsable_compte = responsable
                except User.DoesNotExist:
                    pass
            
            client.save()
            
            messages.success(request, f"Client {client.nom} modifié avec succès!")
            return redirect('fiche_client', client_id=client.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/modifier_client.html', {'client': client})

@login_required
def SupprimerClientView(request, client_id):
    """Vue pour supprimer un client"""
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        try:
            nom_client = client.nom
            client.delete()
            messages.success(request, f"Client {nom_client} supprimé avec succès!")
            return redirect('clients')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'administration/supprimer_client.html', {'client': client})
