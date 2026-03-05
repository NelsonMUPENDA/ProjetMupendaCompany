from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum, Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.views import generic
from datetime import timedelta, datetime
try:
    from django.contrib.sessions.models import Session
except Exception:
    Session = None
from .models import (
    Client, Projet, SuiviTemps, AffectationCollaborateur, 
    Services, Apropos, Realisation, Post, Contact, TemoignageClient, Category,
    CustomUser, Role, Permission, UserRole, Departement, Tache, Notification, LogAction,
    Partenaire, FAQ, PageLegale, Devis, NewsletterSubscriber, SiteContact
)
from .forms import (
    FormationForm, UserForm, InsertApropos,
    DepartementForm, ProjetForm, TacheForm, UserAdminForm, UserRoleForm
)

try:
    from .models import Facture, LigneFacture, Collaborateur, TicketSupport, MessageTicket
except ImportError:
    Facture = None
    LigneFacture = None
    Collaborateur = None
    TicketSupport = None
    MessageTicket = None


def _get_active_role_from_session(request):
    return request.session.get('active_role')


def _user_has_any_permission(user, *permission_codes):
    if user.is_super_admin():
        return True
    return any(user.has_permission(code) for code in permission_codes)


def _require_roles(request, allowed_roles):
    if request.user.is_super_admin():
        return True

    active_role = _get_active_role_from_session(request) or request.user.get_primary_role()
    return active_role in set(allowed_roles)


def _forbidden(request):
    messages.error(request, "Accès refusé.")
    return redirect('connexion')


@login_required
def analytics_center(request):
    """Vue pour le centre d'analytics - Super Admin"""
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)
    
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(est_actif=True).count()
    
    # KPIs simulés pour l'instant
    kpis = {
        'revenue': 150000,
        'new_customers': 1200,
        'churn_rate': 5.2,
        'system_health': 92,
    }
    
    # Rapports récents
    recent_reports = LogAction.objects.order_by('-date_action')[:5]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'kpis': kpis,
        'recent_reports': recent_reports,
        'page_title': 'Centre d\'Analytics'
    }
    return render(request, 'dashboard/super_admin/analytics_center.html', context)


# Create your views here.
class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blog.html'
    context_object_name = 'object_list'
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.filter(status=1).order_by('-created_on')
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ['Technologie', 'Innovation', 'Business', 'Cybersécurité', 'Cloud', 'IA & Data']
        context['current_category'] = self.request.GET.get('category', '')
        return context


def load_more_posts(request):
    """AJAX endpoint for loading more posts"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    page = int(request.GET.get('page', 2))
    category = request.GET.get('category', '')
    
    posts = Post.objects.filter(status=1)
    if category:
        posts = posts.filter(category=category)
    posts = posts.order_by('-created_on')
    
    # Paginate
    from django.core.paginator import Paginator
    paginator = Paginator(posts, 6)
    
    try:
        page_obj = paginator.page(page)
    except:
        return JsonResponse({'html': '', 'has_more': False})
    
    # Render posts HTML
    posts_data = []
    for post in page_obj.object_list:
        posts_data.append({
            'titre': post.titre,
            'slug': post.slug,
            'category': post.category,
            'content': post.content[:150] + '...' if len(post.content) > 150 else post.content,
            'image_url': post.image.url if post.image else '/static/images/default-blog.jpg',
            'created_on': post.created_on.strftime('%d %b %Y'),
            'timesince': post.created_on.strftime('%d %b %Y')
        })
    
    has_more = page_obj.has_next()
    
    return JsonResponse({
        'posts': posts_data,
        'has_more': has_more,
        'next_page': page + 1 if has_more else None
    })

class BlogDetailView(generic.DetailView):
    model = Post
    template_name = 'blog_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related posts (same category, excluding current post)
        current_post = self.get_object()
        related_posts = Post.objects.filter(
            category=current_post.category,
            status=1
        ).exclude(
            id=current_post.id
        ).order_by('-created_on')[:4]
        
        # If not enough related posts, get recent posts
        if related_posts.count() < 4:
            existing_ids = list(related_posts.values_list('id', flat=True)) + [current_post.id]
            additional_posts = Post.objects.filter(
                status=1
            ).exclude(
                id__in=existing_ids
            ).order_by('-created_on')[:(4 - related_posts.count())]
            related_posts = list(related_posts) + list(additional_posts)
        
        context['related_posts'] = related_posts
        return context

class FormationList(generic.ListView):
    queryset = Formation.objects.filter(status=1).order_by ('-date_debut')
    template_name = 'formation.html'

class FormationDetailView(generic.DetailView):
    model = Formation
    template_name = 'detail_formation.html'
    context_object_name = 'formation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get other formations (excluding current formation)
        current_formation = self.get_object()
        other_formations = Formation.objects.filter(
            status=1
        ).exclude(
            id=current_formation.id
        ).order_by('-date_debut')[:4]
        context['other_formations'] = other_formations
        return context


class RealisationDetailView(generic.DetailView):
    model = Realisation
    template_name = 'realisation_detail.html'
    context_object_name = 'realisation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related realisations (same category, excluding current)
        current_realisation = self.get_object()
        related_realisations = Realisation.objects.filter(
            category=current_realisation.category,
            status=True
        ).exclude(
            id=current_realisation.id
        ).order_by('-created_on')[:4]
        context['related_realisations'] = related_realisations
        return context

def index(request):
    service = Services.objects.all().order_by('-date_ajout')[:7]
    afficher = Realisation.objects.filter(status=True).order_by('-created_on')[:4]
    afficherApropos = Apropos.objects.filter(est_actif=True).first()
    temoignages = TemoignageClient.objects.filter(status=True).order_by('-created_on')[:6]
    partenaires = Partenaire.objects.filter(est_actif=True).order_by('ordre_affichage')[:8]
    return render(request, 'index.html', {
        'afficherApropos': afficherApropos,
        'service': service,
        'afficher': afficher,
        'temoignages': temoignages,
        'partenaires': partenaires
    })

#Inscription
User = get_user_model()

def inscription(request):
    form = UserForm()
    if request.method == "POST":
        form = UserForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    return render(request, 'dashboard/inscription.html', {'form': form})


def get_user_roles_ajax(request):
    """
    Vue AJAX pour récupérer les rôles d'un utilisateur par son username ou email.
    Utilisé pour peupler dynamiquement le dropdown des rôles sur la page de connexion.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
    
    username_or_email = request.POST.get('username', '').strip()
    
    if not username_or_email:
        return JsonResponse({'success': False, 'message': 'Veuillez entrer un nom d\'utilisateur ou email'})
    
    # Vérification du format de l'email ou username
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    
    is_email = False
    try:
        validate_email(username_or_email)
        is_email = True
    except ValidationError:
        pass
    
    # Recherche de l'utilisateur
    User = get_user_model()
    try:
        if is_email:
            user = User.objects.get(email__iexact=username_or_email)
        else:
            user = User.objects.get(username__iexact=username_or_email)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé'})
    
    # Vérifier si l'utilisateur est banni
    if user.is_banned():
        return JsonResponse({'success': False, 'message': 'Compte bloqué ou désactivé'})
    
    # Récupérer les rôles actifs de l'utilisateur
    user_roles = user.user_roles.filter(est_actif=True).select_related('role')
    
    roles_data = []
    for user_role in user_roles:
        role = user_role.role
        roles_data.append({
            'nom': role.nom,
            'nom_display': role.get_nom_display(),
            'niveau_hierarchique': role.niveau_hierarchique,
            'description': role.description or '',
        })
    
    # Trier par niveau hiérarchique décroissant
    roles_data.sort(key=lambda x: x['niveau_hierarchique'], reverse=True)
    
    return JsonResponse({
        'success': True,
        'roles': roles_data,
        'user_found': True,
        'username': user.username,
        'has_multiple_roles': len(roles_data) > 1,
    })


# Connexion avec gestion avancée des rôles et sécurité

def connexion(request):
    erreur = ''
    
    if request.method == "POST":
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        selected_role = request.POST.get('role', '').strip()
        remember_me = request.POST.get('remember_me') == 'on'
        
        # Validation basique - uniquement username et password obligatoires
        if not username_or_email or not password:
            erreur = 'Veuillez entrer votre identifiant et mot de passe'
            return render(request, 'dashboard/connexion.html', {'erreur': erreur, 'username': username_or_email})
        
        # Vérification du format de l'email ou username
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        is_email = False
        try:
            validate_email(username_or_email)
            is_email = True
        except ValidationError:
            pass
        
        # Recherche de l'utilisateur
        User = get_user_model()
        try:
            if is_email:
                user = User.objects.get(email__iexact=username_or_email)
            else:
                user = User.objects.get(username__iexact=username_or_email)
        except User.DoesNotExist:
            erreur = 'Identifiants incorrects'
            return render(request, 'dashboard/connexion.html', {'erreur': erreur, 'username': username_or_email})
        
        # Vérification si l'utilisateur est banni
        if user.is_banned():
            if user.bloque_jusqua and user.bloque_jusqua > timezone.now():
                temps_restant = user.bloque_jusqua - timezone.now()
                minutes = int(temps_restant.total_seconds() / 60)
                erreur = f'Compte temporairement bloqué. Réessayez dans {minutes} minutes'
            else:
                erreur = 'Compte désactivé. Veuillez contacter l\'administrateur'
            return render(request, 'dashboard/connexion.html', {'erreur': erreur, 'username': username_or_email})
        
        # Authentification
        authenticated_user = authenticate(request, username=user.username, password=password)
        
        if authenticated_user is not None:
            # Si un rôle est sélectionné, vérifier qu'il est valide
            if selected_role:
                user_role = authenticated_user.user_roles.filter(
                    role__nom=selected_role,
                    est_actif=True
                ).first()
                
                if not user_role:
                    erreur = f'Vous n\'avez pas le rôle {selected_role} ou ce rôle n\'est pas actif'
                    authenticated_user.tentative_echec += 1
                    if authenticated_user.tentative_echec >= 5:
                        authenticated_user.bloque_jusqua = timezone.now() + timezone.timedelta(minutes=30)
                        authenticated_user.tentative_echec = 0
                        erreur = 'Trop de tentatives échouées. Compte bloqué pour 30 minutes'
                    authenticated_user.save()
                    return render(request, 'dashboard/connexion.html', {'erreur': erreur, 'username': username_or_email, 'selected_role': selected_role})
                
                # Vérification si le rôle est expiré
                if user_role.is_expired():
                    erreur = 'Votre rôle a expiré. Veuillez contacter l\'administrateur'
                    return render(request, 'dashboard/connexion.html', {'erreur': erreur, 'username': username_or_email, 'selected_role': selected_role})
            
            # Connexion de l'utilisateur
            login(request, authenticated_user)

            # Stocker le rôle actif choisi (si un rôle est sélectionné)
            if selected_role:
                request.session['active_role'] = selected_role
            
            # Mise à jour des informations de connexion
            authenticated_user.derniere_connexion = timezone.now()
            authenticated_user.tentative_echec = 0
            authenticated_user.bloque_jusqua = None
            authenticated_user.save()
            
            # Gestion du "Se souvenir de moi"
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semaines
            else:
                request.session.set_expiry(0)  # Session navigateur
            
            # Redirection selon le rôle sélectionné ou vers profil par défaut
            # Vérifier si un paramètre 'next' est présent pour redirection personnalisée
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            elif selected_role == 'SUPER_ADMIN':
                return redirect('super_admin_dashboard')
            elif selected_role == 'ADMINISTRATEUR':
                return redirect('dashboard')
            elif selected_role in ['CHEF_PROJET', 'DEVELOPPEUR', 'DESIGNER', 'COMMERCIAL', 'COMPTABLE', 'RH', 'SUPPORT']:
                return redirect('employe_dashboard')
            elif selected_role == 'FORMATEUR':
                return redirect('formateur_dashboard')
            elif selected_role == 'CLIENT':
                return redirect('client_dashboard')
            elif selected_role == 'COLLABORATEUR':
                return redirect('collaborateur_dashboard')
            elif selected_role == 'STAGIAIRE':
                return redirect('stagiaire_dashboard')
            else:
                # Aucun rôle sélectionné ou rôle non reconnu -> profil standard
                return redirect('profil')
        else:
            # Incrémenter le compteur de tentatives échouées
            user.tentative_echec += 1
            if user.tentative_echec >= 5:
                user.bloque_jusqua = timezone.now() + timezone.timedelta(minutes=30)
                user.tentative_echec = 0
                erreur = 'Trop de tentatives échouées. Compte bloqué pour 30 minutes'
            else:
                tentatives_restantes = 5 - user.tentative_echec
                erreur = f'Mot de passe incorrect. Il vous reste {tentatives_restantes} tentative(s)'
            user.save()
    
    return render(request, 'dashboard/connexion.html', {'erreur': erreur, 'next': request.GET.get('next', '')})


# Vues de redirection selon les rôles

@login_required
def super_admin_dashboard(request):
    """Tableau de bord Super Administrateur"""
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)
    
    # Statistiques globales du système
    from django.utils import timezone
    from datetime import timedelta
    
    # Statistiques utilisateurs
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(est_actif=True).count()
    
    # Utilisateurs bannis
    banned_users = CustomUser.objects.filter(
        Q(est_actif=False) | 
        Q(bloque_jusqua__isnull=False, bloque_jusqua__gt=timezone.now())
    ).distinct().count()
    
    new_users_this_month = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Statistiques rôles et permissions
    total_roles = Role.objects.count()
    active_roles = Role.objects.filter(est_actif=True).count()
    total_permissions = Permission.objects.count()
    
    # Statistiques départements
    total_departements = Departement.objects.count()
    active_departements = Departement.objects.filter(est_actif=True).count()
    
    # Statistiques projets
    total_projects = Projet.objects.count()
    active_projects = Projet.objects.filter(est_actif=True).count()
    completed_projects = Projet.objects.filter(statut='TERMINE').count()
    
    # Statistiques tâches
    total_tasks = Tache.objects.count()
    completed_tasks = Tache.objects.filter(statut='TERMINE').count()
    pending_tasks = Tache.objects.filter(statut='A_FAIRE').count()
    
    # Notifications non lues
    unread_notifications = Notification.objects.filter(
        destinataire=request.user,
        est_lue=False
    ).count()
    
    # Activité récente (logs)
    recent_logs = LogAction.objects.select_related('utilisateur').order_by('-date_action')[:10]
    
    # Projets récents
    recent_projects = Projet.objects.select_related('chef_projet', 'departement').order_by('-date_creation')[:5]
    
    # Sessions actives (simulation - pourrait être basé sur des métriques réelles)
    active_sessions = CustomUser.objects.filter(
        derniere_connexion__gte=timezone.now() - timedelta(minutes=30)
    ).count()
    
    # Croissances (simulation)
    user_growth = "+12%"
    role_growth = "+5%"
    permission_growth = "+8%"
    
    session_change = "-3%"
    session_change_class = "negative"
    session_change_direction = "down"
    
    # Croissance des projets (simulation)
    project_growth = "+8%"
    
    # Santé du système (simulation - pourrait être basé sur des métriques réelles)
    system_health = 98
    system_status = "Optimal"
    
    # Rôles avec détails
    roles = Role.objects.all().order_by('-niveau_hierarchique')
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'banned_users': banned_users,
        'new_users_this_month': new_users_this_month,
        'total_roles': total_roles,
        'active_roles': active_roles,
        'total_permissions': total_permissions,
        'active_sessions': active_sessions,
        'total_departements': total_departements,
        'active_departements': active_departements,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'unread_notifications': unread_notifications,
        'recent_logs': recent_logs,
        'recent_projects': recent_projects,
        'departments': Departement.objects.all()[:5],  # Pour le template
        'user_growth': user_growth,
        'role_growth': role_growth,
        'permission_growth': permission_growth,
        'session_change': session_change,
        'session_change_class': session_change_class,
        'session_change_direction': session_change_direction,
        'project_growth': project_growth,
        'system_health': system_health,
        'system_status': system_status,
        'roles': roles,
        'user_role': 'SUPER_ADMIN',
        'page_title': 'Tableau de Bord Super Administrateur'
    }
    return render(request, 'dashboard/super_admin/dashboard.html', context)


@login_required
def super_admin_manage_users(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    users_qs = CustomUser.objects.all().prefetch_related('user_roles__role').order_by('-date_joined')

    q = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()
    status = request.GET.get('status', '').strip()

    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    if role:
        users_qs = users_qs.filter(user_roles__role__nom=role, user_roles__est_actif=True)

    now = timezone.now()
    if status == 'active':
        users_qs = users_qs.filter(est_actif=True).filter(Q(bloque_jusqua__isnull=True) | Q(bloque_jusqua__lte=now))
    elif status == 'inactive':
        users_qs = users_qs.filter(est_actif=False)
    elif status == 'banned':
        users_qs = users_qs.filter(Q(est_actif=False) | Q(bloque_jusqua__gt=now))

    paginator = Paginator(users_qs.distinct(), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'users': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(est_actif=True).count(),
        'super_admins': CustomUser.objects.filter(user_roles__role__nom='SUPER_ADMIN', user_roles__est_actif=True).distinct().count(),
        'new_users_today': CustomUser.objects.filter(date_joined__date=timezone.now().date()).count(),
        'roles': Role.objects.filter(est_actif=True).order_by('-niveau_hierarchique', 'nom'),
        'now': timezone.now(),
        'querystring': querystring,
        'filters': {
            'q': q,
            'role': role,
            'status': status,
        }
    }
    return render(request, 'dashboard/super_admin/manage_users.html', context)


@login_required
def super_admin_manage_roles(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    roles_qs = Role.objects.all().order_by('-niveau_hierarchique', 'nom')
    context = {
        'roles': roles_qs,
        'total_roles': roles_qs.count(),
        'active_roles': roles_qs.filter(est_actif=True).count(),
        'total_permissions': Permission.objects.count(),
        'role_assignments': UserRole.objects.filter(est_actif=True).count(),
    }
    return render(request, 'dashboard/super_admin/manage_roles.html', context)


@login_required
def super_admin_manage_permissions(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    permissions_qs = Permission.objects.all().order_by('categorie', 'nom')
    
    # Pagination
    paginator = Paginator(permissions_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()
    
    context = {
        'permissions': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': querystring,
        'total_permissions': permissions_qs.count(),
        'active_permissions': permissions_qs.filter(est_active=True).count(),
        'total_modules': permissions_qs.values('categorie').distinct().count(),
        'permission_assignments': Role.permissions.through.objects.count(),
    }
    return render(request, 'dashboard/super_admin/manage_permissions.html', context)


@login_required
def sessions_management(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    sessions_qs = []
    if Session is not None:
        try:
            sessions_qs = Session.objects.all().order_by('-expire_date')
        except Exception:
            sessions_qs = []

    now = timezone.now()
    sessions_data = []
    user_ids = set()

    for s in sessions_qs[:500]:
        try:
            decoded = s.get_decoded()
        except Exception:
            decoded = {}
        user_id = decoded.get('_auth_user_id')
        if user_id:
            user_ids.add(user_id)

    users_by_id = {}
    if user_ids:
        users_by_id = {str(u.id): u for u in CustomUser.objects.filter(id__in=list(user_ids))}

    for s in sessions_qs[:500]:
        try:
            decoded = s.get_decoded()
        except Exception:
            decoded = {}
        user_id = decoded.get('_auth_user_id')
        user = users_by_id.get(str(user_id)) if user_id else None

        computed_status = 'active' if s.expire_date >= now else 'expired'
        username = user.username if user else 'Inconnu'
        email = user.email if user else ''

        if status and status != computed_status:
            continue
        if q and q.lower() not in f"{username} {email} {s.session_key}".lower():
            continue

        sessions_data.append({
            'session_key': s.session_key,
            'expire_date': s.expire_date,
            'status': computed_status,
            'username': username,
            'email': email,
        })

    unique_users = len({row['username'] for row in sessions_data if row['username'] != 'Inconnu'})

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    return render(request, 'dashboard/super_admin/sessions_management.html', {
        'sessions_data': sessions_data,
        'total_sessions': len(sessions_data),
        'active_sessions': len([s for s in sessions_data if s['status'] == 'active']),
        'expired_sessions': len([s for s in sessions_data if s['status'] == 'expired']),
        'unique_users': unique_users,
        'querystring': querystring,
        'filters': {
            'q': q,
            'status': status,
        }
    })


@login_required
def terminate_session(request, session_key):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    if Session is None:
        return JsonResponse({'success': False, 'message': 'Module sessions indisponible'})

    try:
        session = Session.objects.get(session_key=session_key)
    except Session.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Session introuvable'})

    session.delete()

    LogAction.objects.create(
        utilisateur=request.user,
        action='SUPPRESSION',
        modele='Session',
        id_objet=None,
        description=f'Suppression de la session {session_key}',
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, "Session terminée avec succès")
    return redirect('sessions_management')


@login_required
def security_dashboard(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    now = timezone.now()
    banned_users = CustomUser.objects.filter(Q(est_actif=False) | Q(bloque_jusqua__gt=now)).distinct()
    users_high_failures = CustomUser.objects.filter(tentative_echec__gte=3).distinct()

    active_sessions = 0
    if Session is not None:
        try:
            active_sessions = Session.objects.filter(expire_date__gte=now).count()
        except Exception:
            active_sessions = 0

    recent_activity = LogAction.objects.select_related('utilisateur').order_by('-date_action')[:10]

    alerts = []
    if users_high_failures.exists():
        alerts.append({
            'level': 'danger',
            'title': "Tentatives de connexion échouées",
            'description': f"{users_high_failures.count()} utilisateur(s) ont >= 3 tentatives échouées",
        })
    if banned_users.exists():
        alerts.append({
            'level': 'warning',
            'title': "Comptes bloqués ou inactifs",
            'description': f"{banned_users.count()} compte(s) bloqués/inactifs",
        })

    critical_actions_week = LogAction.objects.filter(action='SUPPRESSION', date_action__gte=now - timedelta(days=7)).count()

    context = {
        'alerts': alerts,
        'banned_users_count': banned_users.count(),
        'high_failures_count': users_high_failures.count(),
        'active_sessions_count': active_sessions,
        'critical_actions_week': critical_actions_week,
        'now': now,
        'recent_activity': recent_activity,
    }
    return render(request, 'dashboard/super_admin/security_dashboard.html', context)


@login_required
def export_super_admin_users(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    import csv
    from django.http import HttpResponse

    users_qs = CustomUser.objects.all().prefetch_related('user_roles__role').order_by('-date_joined')

    q = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()
    status = request.GET.get('status', '').strip()

    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    if role:
        users_qs = users_qs.filter(user_roles__role__nom=role, user_roles__est_actif=True)

    now = timezone.now()
    if status == 'active':
        users_qs = users_qs.filter(est_actif=True).filter(Q(bloque_jusqua__isnull=True) | Q(bloque_jusqua__lte=now))
    elif status == 'inactive':
        users_qs = users_qs.filter(est_actif=False)
    elif status == 'banned':
        users_qs = users_qs.filter(Q(est_actif=False) | Q(bloque_jusqua__gt=now))

    users_qs = users_qs.distinct()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Nom complet', 'Roles actifs', 'Statut', 'Date inscription', 'Dernière connexion'])

    for u in users_qs:
        active_roles = [ur.role.nom for ur in u.user_roles.all() if ur.est_actif]
        is_banned = (not u.est_actif) or (u.bloque_jusqua and u.bloque_jusqua > now)
        writer.writerow([
            u.id,
            u.username,
            u.email,
            u.get_full_name(),
            ",".join(active_roles),
            'BANNI/BLOQUE' if is_banned else 'ACTIF',
            u.date_joined.strftime('%Y-%m-%d %H:%M:%S') if u.date_joined else '',
            u.last_login.strftime('%Y-%m-%d %H:%M:%S') if u.last_login else '',
        ])

    LogAction.objects.create(
        utilisateur=request.user,
        action='EXPORTATION',
        modele='CustomUser',
        id_objet=None,
        description='Export CSV des utilisateurs (Super Admin)',
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    return response


@login_required
def audit_logs(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    logs_qs = LogAction.objects.select_related('utilisateur').order_by('-date_action')

    q = request.GET.get('q', '').strip()
    action = request.GET.get('action', '').strip()
    user_id = request.GET.get('user_id', '').strip()
    period = request.GET.get('period', '').strip()

    if q:
        logs_qs = logs_qs.filter(
            Q(utilisateur__username__icontains=q) |
            Q(description__icontains=q) |
            Q(modele__icontains=q) |
            Q(adresse_ip__icontains=q)
        )

    if action:
        logs_qs = logs_qs.filter(action=action)

    if user_id:
        logs_qs = logs_qs.filter(utilisateur_id=user_id)

    now = timezone.now()
    if period == 'today':
        logs_qs = logs_qs.filter(date_action__date=now.date())
    elif period == 'week':
        logs_qs = logs_qs.filter(date_action__gte=now - timedelta(days=7))
    elif period == 'month':
        logs_qs = logs_qs.filter(date_action__gte=now - timedelta(days=30))
    elif period == 'year':
        logs_qs = logs_qs.filter(date_action__gte=now - timedelta(days=365))

    paginator = Paginator(logs_qs, 50)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    stats_total = LogAction.objects.count()
    stats_today = LogAction.objects.filter(date_action__date=now.date()).count()
    stats_week = LogAction.objects.filter(date_action__gte=now - timedelta(days=7)).count()
    stats_critical = LogAction.objects.filter(action='SUPPRESSION').count()

    users_for_filter = CustomUser.objects.filter(logs_actions__isnull=False).distinct().order_by('username')

    return render(request, 'dashboard/super_admin/audit_logs.html', {
        'logs': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'users_for_filter': users_for_filter,
        'action_choices': LogAction.ACTION_CHOICES,
        'querystring': querystring,
        'filters': {
            'q': q,
            'action': action,
            'user_id': user_id,
            'period': period,
        },
        'stats': {
            'total': stats_total,
            'today': stats_today,
            'week': stats_week,
            'critical': stats_critical,
        }
    })


@login_required
def maintenance_center(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    now = timezone.now()
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(est_actif=True).count()
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(est_lue=False).count()
    total_logs = LogAction.objects.count()
    logs_7d = LogAction.objects.filter(date_action__gte=now - timedelta(days=7)).count()

    active_sessions = 0
    if Session is not None:
        try:
            active_sessions = Session.objects.filter(expire_date__gte=now).count()
        except Exception:
            active_sessions = 0

    context = {
        'now': now,
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'total_logs': total_logs,
            'logs_7d': logs_7d,
            'active_sessions': active_sessions,
        }
    }
    return render(request, 'dashboard/super_admin/maintenance_center.html', context)


@login_required
def super_admin_maintenance_action(request, action_code):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    allowed_actions = {
        'refresh',
        'optimize_db', 'vacuum_db', 'cleanup_db',
        'create_backup', 'schedule_backup', 'restore_backup', 'download_backup', 'delete_backup',
        'clear_cache', 'restart_services', 'optimize_performance',
        'security_scan', 'apply_patches', 'update_firewall',
        'rotate_logs', 'compress_logs', 'cleanup_logs',
        'validate_config', 'export_config', 'import_config',
        'run_full_diagnostic',
    }
    if action_code not in allowed_actions:
        return JsonResponse({'success': False, 'message': 'Action inconnue'})

    item = request.POST.get('item')
    item_part = f" (item={item})" if item else ""

    LogAction.objects.create(
        utilisateur=request.user,
        action='AUTRE',
        modele='Maintenance',
        id_objet=None,
        description=f'Action maintenance: {action_code}{item_part}',
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, "Action de maintenance enregistrée")
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('maintenance_center')


@login_required
def notifications_center(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    qs = Notification.objects.select_related('destinataire').all().order_by('-date_creation')

    q = request.GET.get('q', '').strip()
    type_notification = request.GET.get('type', '').strip()
    status = request.GET.get('status', '').strip()  # read/unread
    period = request.GET.get('period', '').strip()  # today/week/month

    if q:
        qs = qs.filter(
            Q(titre__icontains=q) |
            Q(message__icontains=q) |
            Q(destinataire__username__icontains=q) |
            Q(destinataire__email__icontains=q)
        )

    if type_notification:
        qs = qs.filter(type_notification=type_notification)

    if status == 'unread':
        qs = qs.filter(est_lue=False)
    elif status == 'read':
        qs = qs.filter(est_lue=True)

    now = timezone.now()
    if period == 'today':
        qs = qs.filter(date_creation__date=now.date())
    elif period == 'week':
        qs = qs.filter(date_creation__gte=now - timedelta(days=7))
    elif period == 'month':
        qs = qs.filter(date_creation__gte=now - timedelta(days=30))

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    total_all = Notification.objects.count()
    unread_all = Notification.objects.filter(est_lue=False).count()
    info_all = Notification.objects.filter(type_notification='INFO').count()
    warning_all = Notification.objects.filter(type_notification='AVERTISSEMENT').count()
    error_all = Notification.objects.filter(type_notification='ERREUR').count()
    system_all = Notification.objects.filter(type_notification='SYSTEME').count()

    read_rate = 0
    if total_all:
        read_rate = int(((total_all - unread_all) / total_all) * 100)

    return render(request, 'dashboard/super_admin/notifications_center.html', {
        'notifications': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': querystring,
        'types': Notification.TYPE_CHOICES,
        'filters': {
            'q': q,
            'type': type_notification,
            'status': status,
            'period': period,
        },
        'stats': {
            'total': total_all,
            'unread': unread_all,
            'info': info_all,
            'warning': warning_all,
            'error': error_all,
            'system': system_all,
            'read_rate': read_rate,
        }
    })


@login_required
def super_admin_notification_mark_read(request, notification_id):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    notification = get_object_or_404(Notification, id=notification_id)
    if not notification.est_lue:
        notification.marquer_comme_lue()

        LogAction.objects.create(
            utilisateur=request.user,
            action='MODIFICATION',
            modele='Notification',
            id_objet=notification.id,
            description=f"Marquer notification comme lue: {notification.titre}",
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

    messages.success(request, 'Notification marquée comme lue')
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('notifications_center')


@login_required
def super_admin_notifications_mark_all_read(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    now = timezone.now()
    updated = Notification.objects.filter(est_lue=False).update(est_lue=True, date_lecture=now)

    LogAction.objects.create(
        utilisateur=request.user,
        action='MODIFICATION',
        modele='Notification',
        id_objet=None,
        description=f"Marquer toutes les notifications comme lues ({updated})",
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, f"{updated} notification(s) marquée(s) comme lue(s)")
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('notifications_center')


@login_required
def super_admin_notification_delete(request, notification_id):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    notification = get_object_or_404(Notification, id=notification_id)
    titre = notification.titre
    notification.delete()

    LogAction.objects.create(
        utilisateur=request.user,
        action='SUPPRESSION',
        modele='Notification',
        id_objet=notification_id,
        description=f"Suppression notification: {titre}",
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, 'Notification supprimée')
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('notifications_center')


@login_required
def super_admin_notifications_clear_all(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    deleted, _ = Notification.objects.all().delete()

    LogAction.objects.create(
        utilisateur=request.user,
        action='SUPPRESSION',
        modele='Notification',
        id_objet=None,
        description=f"Suppression de toutes les notifications ({deleted})",
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, 'Toutes les notifications ont été supprimées')
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('notifications_center')


@login_required
def super_admin_notifications_export(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    import csv

    qs = Notification.objects.select_related('destinataire').all().order_by('-date_creation')
    q = request.GET.get('q', '').strip()
    type_notification = request.GET.get('type', '').strip()
    status = request.GET.get('status', '').strip()
    period = request.GET.get('period', '').strip()

    if q:
        qs = qs.filter(
            Q(titre__icontains=q) |
            Q(message__icontains=q) |
            Q(destinataire__username__icontains=q) |
            Q(destinataire__email__icontains=q)
        )
    if type_notification:
        qs = qs.filter(type_notification=type_notification)
    if status == 'unread':
        qs = qs.filter(est_lue=False)
    elif status == 'read':
        qs = qs.filter(est_lue=True)

    now = timezone.now()
    if period == 'today':
        qs = qs.filter(date_creation__date=now.date())
    elif period == 'week':
        qs = qs.filter(date_creation__gte=now - timedelta(days=7))
    elif period == 'month':
        qs = qs.filter(date_creation__gte=now - timedelta(days=30))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="notifications_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Destinataire', 'Type', 'Titre', 'Message', 'Lu', 'Lien'])

    for n in qs[:5000]:
        writer.writerow([
            n.date_creation.strftime('%Y-%m-%d %H:%M:%S'),
            n.destinataire.username if n.destinataire_id else '',
            n.type_notification,
            n.titre,
            n.message,
            'OUI' if n.est_lue else 'NON',
            n.lien or '',
        ])

    LogAction.objects.create(
        utilisateur=request.user,
        action='EXPORTATION',
        modele='Notification',
        id_objet=None,
        description='Export CSV des notifications',
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    return response


@login_required
def super_admin_profile(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    recent_activity = LogAction.objects.select_related('utilisateur').order_by('-date_action')[:10]
    
    # Get user's active sessions
    user_sessions = []
    current_session_key = request.session.session_key
    
    if Session is not None:
        try:
            all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            for session in all_sessions:
                try:
                    decoded = session.get_decoded()
                    user_id = decoded.get('_auth_user_id')
                    if user_id and str(user_id) == str(request.user.id):
                        user_sessions.append({
                            'session_key': session.session_key,
                            'is_current': session.session_key == current_session_key,
                            'ip': decoded.get('_auth_user_ip', request.META.get('REMOTE_ADDR')),
                            'device': decoded.get('_auth_user_agent', request.META.get('HTTP_USER_AGENT', ''))[:50],
                            'last_activity': session.expire_date - timedelta(days=14) if session.expire_date else None,
                        })
                except Exception:
                    continue
        except Exception:
            pass

    return render(request, 'dashboard/super_admin/profile.html', {
        'recent_activity': recent_activity,
        'user_sessions': user_sessions,
    })


@login_required
def super_admin_profile_update(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    user = request.user
    with transaction.atomic():
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.telephone = request.POST.get('telephone', '').strip() or None

        date_embauche_raw = request.POST.get('date_embauche', '').strip()
        if date_embauche_raw:
            try:
                user.date_embauche = datetime.strptime(date_embauche_raw, '%Y-%m-%d').date()
            except Exception:
                messages.error(request, "Date d'embauche invalide")
        else:
            user.date_embauche = None

        if request.FILES.get('photo_profil'):
            user.photo_profil = request.FILES.get('photo_profil')

        user.save()

    LogAction.objects.create(
        utilisateur=request.user,
        action='MODIFICATION',
        modele='CustomUser',
        id_objet=request.user.id,
        description='Mise à jour du profil Super Admin',
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, 'Profil mis à jour')
    return redirect('super_admin_profile')


@login_required
def super_admin_password_update(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    current_password = request.POST.get('current_password', '')
    new_password = request.POST.get('new_password', '')
    confirm_password = request.POST.get('confirm_password', '')

    if not request.user.check_password(current_password):
        messages.error(request, 'Mot de passe actuel incorrect')
        return redirect('super_admin_profile')

    if not new_password or new_password != confirm_password:
        messages.error(request, 'Les mots de passe ne correspondent pas')
        return redirect('super_admin_profile')

    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)

    LogAction.objects.create(
        utilisateur=request.user,
        action='MODIFICATION',
        modele='CustomUser',
        id_objet=request.user.id,
        description='Changement de mot de passe (Super Admin)',
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, 'Mot de passe mis à jour')
    return redirect('super_admin_profile')


@login_required
def super_admin_preferences_update(request):
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    email_notifications = request.POST.get('emailNotifications') == 'on'
    dark_mode = request.POST.get('darkMode') == 'on'

    # Sauvegarder les préférences en base de données
    user = request.user
    user.pref_email_notifications = email_notifications
    user.pref_dark_mode = dark_mode
    user.save()

    LogAction.objects.create(
        utilisateur=request.user,
        action='MODIFICATION',
        modele='CustomUser',
        id_objet=user.id,
        description='Mise à jour des préférences utilisateur (email_notifications: {}, dark_mode: {})'.format(
            'activé' if email_notifications else 'désactivé',
            'activé' if dark_mode else 'désactivé'
        ),
        adresse_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    messages.success(request, 'Préférences enregistrées dans la base de données')
    return redirect('super_admin_profile')


@login_required
def system_parameters(request):
    """Paramètres du système - Fonctionnalité en développement"""
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)
    
    return render(request, 'dashboard/super_admin/system_parameters.html', {
        'en_developpement': True,
        'titre': 'Paramètres du Système',
        'message': 'Cette fonctionnalité est en cours de développement.',
        'date_prevue': 'Bientôt disponible',
    })


@login_required
def dashboard(request):
    """Tableau de bord Administrateur"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    # Statistiques pour l'administrateur
    from django.utils import timezone
    from datetime import timedelta
    
    # Statistiques utilisateurs (sans voir les Super Admins)
    total_users = CustomUser.objects.exclude(user_roles__role__nom='SUPER_ADMIN').count()
    active_users = CustomUser.objects.filter(
        est_actif=True
    ).exclude(user_roles__role__nom='SUPER_ADMIN').count()
    
    # Statistiques projets
    user_projects = Projet.objects.filter(
        Q(equipe=request.user) | Q(chef_projet=request.user)
    ).distinct()
    
    total_projects = user_projects.count()
    active_projects = user_projects.filter(statut='EN_COURS').count()
    completed_projects = user_projects.filter(statut='TERMINE').count()
    
    # Statistiques tâches
    user_tasks = Tache.objects.filter(assigne_a=request.user)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(statut='TERMINE').count()
    pending_tasks = user_tasks.filter(statut='A_FAIRE').count()
    
    # Notifications
    unread_notifications = Notification.objects.filter(
        destinataire=request.user,
        est_lue=False
    ).count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'unread_notifications': unread_notifications,
        'user_role': 'ADMINISTRATEUR',
        'page_title': 'Tableau de Bord Administrateur'
    }
    
    return render(request, 'dashboard/super_admin/admin_dashboard.html', context)

@login_required
def employe_dashboard(request):
    """Tableau de bord pour les employés (Chef de projet, développeur, etc.)"""
    if not _require_roles(request, {'CHEF_PROJET', 'DEVELOPPEUR', 'DESIGNER', 'COMMERCIAL', 'COMPTABLE', 'RH', 'SUPPORT', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    from django.utils import timezone
    
    # Projets de l'utilisateur
    user_projects = Projet.objects.filter(
        Q(equipe=request.user) | Q(chef_projet=request.user)
    ).distinct()
    
    # Tâches de l'utilisateur
    user_tasks = Tache.objects.filter(assigne_a=request.user)
    
    # Statistiques
    total_projects = user_projects.count()
    active_projects = user_projects.filter(statut='EN_COURS').count()
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(statut='TERMINE').count()
    pending_tasks = user_tasks.filter(statut='A_FAIRE').count()
    overdue_tasks = user_tasks.filter(
        date_echeance__lt=timezone.now().date(),
        statut__in=['A_FAIRE', 'EN_COURS', 'EN_REVISION']
    ).count()
    
    # Notifications
    unread_notifications = Notification.objects.filter(
        destinataire=request.user,
        est_lue=False
    ).count()
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'unread_notifications': unread_notifications,
        'user_role': request.user.get_primary_role(),
        'page_title': f'Tableau de Bord {request.user.get_primary_role()}'
    }
    
    return render(request, 'dashboard/employe/dashboard.html', context)

@login_required
def formateur_dashboard(request):
    """Tableau de bord pour les formateurs"""
    if not _require_roles(request, {'FORMATEUR', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    context = {
        'user_role': 'FORMATEUR',
        'page_title': 'Tableau de Bord Formateur'
    }
    return render(request, 'dashboard/formateur/dashboard.html', context)

# Vues pour la gestion complète de l'entreprise
@login_required
def gestion_departements(request):
    """Vue pour la gestion des départements"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'DEPARTEMENT_AJOUTER', 'DEPARTEMENT_MODIFIER', 'DEPARTEMENT_SUPPRIMER'):
        return _forbidden(request)
    
    departements = Departement.objects.all().order_by('nom')
    context = {
        'departements': departements,
        'page_title': 'Gestion des Départements'
    }
    return render(request, 'dashboard/departements/list.html', context)

@login_required
def creer_departement(request):
    """Vue pour créer un département"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'DEPARTEMENT_AJOUTER'):
        return _forbidden(request)
    
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            departement = form.save()
            LogAction.objects.create(
                utilisateur=request.user,
                action='CREATION',
                modele='Departement',
                id_objet=departement.id,
                description=f'Création du département {departement.nom}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('gestion_departements')
    else:
        form = DepartementForm()
    
    return render(request, 'dashboard/departements/form.html', {'form': form})

@login_required
def gestion_projets(request):
    """Vue pour la gestion des projets"""
    if not _require_roles(request, {'CHEF_PROJET', 'DEVELOPPEUR', 'DESIGNER', 'COMMERCIAL', 'COMPTABLE', 'RH', 'SUPPORT', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    # Filtrer selon le rôle
    if request.user.is_super_admin():
        projets = Projet.objects.all()
    elif request.user.is_admin():
        projets = Projet.objects.all()
    else:
        projets = Projet.objects.filter(
            Q(chef_projet=request.user) | Q(equipe=request.user)
        ).distinct()
    
    context = {
        'projets': projets,
        'page_title': 'Gestion des Projets'
    }
    return render(request, 'dashboard/projets/list.html', context)

@login_required
def creer_projet(request):
    """Vue pour créer un projet"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'PROJET_AJOUTER'):
        return _forbidden(request)
    
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.cree_par = request.user
            projet.save()
            
            # Ajouter l'équipe si spécifiée
            if 'equipe' in request.POST:
                projet.equipe.set(request.POST.getlist('equipe'))
            
            LogAction.objects.create(
                utilisateur=request.user,
                action='CREATION',
                modele='Projet',
                id_objet=projet.id,
                description=f'Création du projet {projet.nom}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('gestion_projets')
    else:
        form = ProjetForm()
    
    return render(request, 'dashboard/projets/form.html', {'form': form})

@login_required
def detail_projet(request, projet_id):
    """Vue pour voir les détails d'un projet"""
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not (request.user.is_super_admin() or 
              request.user.is_admin() or 
              projet.chef_projet == request.user or 
              projet.equipe.filter(id=request.user.id).exists()):
        return redirect('connexion')
    
    taches = Tache.objects.filter(projet=projet).order_by('-date_creation')
    
    context = {
        'projet': projet,
        'taches': taches,
        'page_title': f'Détails du Projet - {projet.nom}'
    }
    return render(request, 'dashboard/projets/detail.html', context)

@login_required
def gestion_taches(request):
    """Vue pour la gestion des tâches"""
    if not _require_roles(request, {'CHEF_PROJET', 'DEVELOPPEUR', 'DESIGNER', 'COMMERCIAL', 'COMPTABLE', 'RH', 'SUPPORT', 'COLLABORATEUR', 'STAGIAIRE', 'FORMATEUR', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    # Filtrer selon le rôle
    if request.user.is_super_admin():
        taches = Tache.objects.all()
    elif request.user.is_admin():
        taches = Tache.objects.all()
    else:
        taches = Tache.objects.filter(
            Q(assigne_a=request.user) | 
            Q(projet__chef_projet=request.user) | 
            Q(projet__equipe=request.user)
        ).distinct()
    
    context = {
        'taches': taches,
        'page_title': 'Gestion des Tâches'
    }
    return render(request, 'dashboard/taches/list.html', context)

@login_required
def creer_tache(request):
    """Vue pour créer une tâche"""
    if not _require_roles(request, {'CHEF_PROJET', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'TACHE_AJOUTER'):
        return _forbidden(request)
    
    if request.method == 'POST':
        form = TacheForm(request.POST)
        if form.is_valid():
            tache = form.save(commit=False)
            tache.cree_par = request.user
            tache.save()
            
            LogAction.objects.create(
                utilisateur=request.user,
                action='CREATION',
                modele='Tache',
                id_objet=tache.id,
                description=f'Création de la tâche {tache.titre}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('gestion_taches')
    else:
        form = TacheForm()
    
    return render(request, 'dashboard/taches/form.html', {'form': form})

@login_required
def gestion_utilisateurs(request):
    """Vue pour la gestion des utilisateurs (Admin)"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'UTILISATEUR_AJOUTER', 'UTILISATEUR_MODIFIER', 'UTILISATEUR_SUPPRIMER'):
        return _forbidden(request)
    
    # Exclure les Super Admins pour les Admins normaux
    if request.user.is_super_admin():
        utilisateurs = CustomUser.objects.all()
    else:
        utilisateurs = CustomUser.objects.exclude(
            user_roles__role__nom='SUPER_ADMIN'
        )
    
    context = {
        'utilisateurs': utilisateurs,
        'page_title': 'Gestion des Utilisateurs'
    }
    return render(request, 'dashboard/utilisateurs/list.html', context)

@login_required
def creer_utilisateur(request):
    """Vue pour créer un utilisateur"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'UTILISATEUR_AJOUTER'):
        return _forbidden(request)
    
    if request.method == 'POST':
        form = UserAdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            LogAction.objects.create(
                utilisateur=request.user,
                action='CREATION',
                modele='CustomUser',
                id_objet=user.id,
                description=f'Création de l\'utilisateur {user.username}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('gestion_utilisateurs')
    else:
        form = UserAdminForm()
    
    return render(request, 'dashboard/utilisateurs/form.html', {'form': form})

@login_required
def assigner_role_utilisateur(request, user_id):
    """Vue pour assigner des rôles à un utilisateur"""
    if not request.user.is_superuser and not request.user.user_roles.filter(role__nom='SUPER_ADMIN').exists():
        messages.error(request, "Vous n'avez pas les permissions nécessaires.")
        return redirect('super_admin_manage_users')
    
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    
    # Récupérer tous les rôles disponibles
    roles = Role.objects.filter(est_actif=True).order_by('-niveau_hierarchique', 'nom')
    
    # Récupérer toutes les permissions
    permissions = Permission.objects.all().order_by('categorie', 'nom')
    
    # Récupérer les permissions actuelles de l'utilisateur (via ses rôles)
    utilisateur_permissions = Permission.objects.filter(
        roles__role_users__utilisateur=utilisateur,
        roles__role_users__est_actif=True
    ).distinct()
    
    if request.method == 'POST':
        action = request.POST.get('action', 'assign')
        
        if action == 'assign':
            role_id = request.POST.get('role')
            est_actif = request.POST.get('est_actif') == 'on'
            
            if role_id:
                try:
                    role = Role.objects.get(id=role_id)
                    # Créer ou mettre à jour le UserRole
                    user_role, created = UserRole.objects.get_or_create(
                        utilisateur=utilisateur,
                        role=role,
                        defaults={
                            'attribue_par': request.user,
                            'est_actif': est_actif
                        }
                    )
                    
                    if not created:
                        # Mettre à jour le statut si le rôle existe déjà
                        user_role.est_actif = est_actif
                        user_role.save()
                        messages.success(request, f"Le rôle {role.get_nom_display()} a été mis à jour.")
                    else:
                        messages.success(request, f"Le rôle {role.get_nom_display()} a été assigné avec succès.")
                    
                    return redirect('assigner_role_utilisateur', user_id=user_id)
                    
                except Role.DoesNotExist:
                    messages.error(request, "Le rôle sélectionné n'existe pas.")
            else:
                messages.error(request, "Veuillez sélectionner un rôle.")
    
    context = {
        'utilisateur': utilisateur,
        'roles': roles,
        'permissions': permissions,
        'utilisateur_permissions': utilisateur_permissions,
        'page_title': f'Assigner un rôle à {utilisateur.username}'
    }
    
    return render(request, 'dashboard/utilisateurs/assigner_role.html', context)


@login_required
def revoquer_role_utilisateur(request, user_id, user_role_id):
    """Vue pour révoquer (supprimer) un rôle d'un utilisateur"""
    if not request.user.is_superuser and not request.user.user_roles.filter(role__nom='SUPER_ADMIN').exists():
        messages.error(request, "Vous n'avez pas les permissions nécessaires.")
        return redirect('super_admin_manage_users')
    
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    user_role = get_object_or_404(UserRole, id=user_role_id, utilisateur=utilisateur)
    
    if request.method == 'POST':
        role_name = user_role.role.get_nom_display()
        user_role.delete()
        
        # Créer un log
        LogAction.objects.create(
            utilisateur=request.user,
            action='SUPPRESSION',
            modele='UserRole',
            id_objet=user_role_id,
            description=f'Révocation du rôle {role_name} pour {utilisateur.username}',
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, f"Le rôle {role_name} a été révoqué avec succès.")
        return redirect('assigner_role_utilisateur', user_id=user_id)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})


@login_required
def toggle_role_status(request, user_id, user_role_id):
    """Vue pour activer/désactiver un rôle d'un utilisateur"""
    if not request.user.is_superuser and not request.user.user_roles.filter(role__nom='SUPER_ADMIN').exists():
        return JsonResponse({'success': False, 'message': "Permissions insuffisantes"})
    
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    user_role = get_object_or_404(UserRole, id=user_role_id, utilisateur=utilisateur)
    
    if request.method == 'POST':
        # Inverser le statut
        user_role.est_actif = not user_role.est_actif
        user_role.save()
        
        action_str = 'activé' if user_role.est_actif else 'désactivé'
        
        # Créer un log
        LogAction.objects.create(
            utilisateur=request.user,
            action='MODIFICATION',
            modele='UserRole',
            id_objet=user_role_id,
            description=f'Rôle {user_role.role.get_nom_display()} {action_str} pour {utilisateur.username}',
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'success': True, 
            'message': f"Rôle {action_str} avec succès",
            'est_actif': user_role.est_actif
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def gestion_notifications(request):
    """Vue pour la gestion des notifications"""
    if not _require_roles(request, {'CHEF_PROJET', 'DEVELOPPEUR', 'DESIGNER', 'COMMERCIAL', 'COMPTABLE', 'RH', 'SUPPORT', 'COLLABORATEUR', 'STAGIAIRE', 'FORMATEUR', 'CLIENT', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    notifications = Notification.objects.filter(
        destinataire=request.user
    ).order_by('-date_creation')
    
    context = {
        'notifications': notifications,
        'page_title': 'Notifications'
    }
    return render(request, 'dashboard/notifications/list.html', context)

@login_required
def marquer_notification_lue(request, notification_id):
    """Vue pour marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, destinataire=request.user)
    notification.marquer_comme_lue()
    
    return JsonResponse({'success': True})

@login_required
def compter_notifications_non_lues(request):
    """Vue pour compter les notifications non lues"""
    count = Notification.objects.filter(
        destinataire=request.user,
        est_lue=False
    ).count()
    
    return JsonResponse({'count': count})

@login_required
def api_notifications_recentes(request):
    """API pour récupérer les notifications récentes pour le dropdown"""
    limit = int(request.GET.get('limit', 5))
    
    notifications = Notification.objects.filter(
        destinataire=request.user
    ).order_by('-date_creation')[:limit]
    
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'titre': notif.titre,
            'message': notif.message,
            'type': notif.type_notification,
            'est_lue': notif.est_lue,
            'date': notif.date_creation.strftime('%d/%m/%Y %H:%M'),
            'lien': notif.lien or '#'
        })
    
    return JsonResponse({'notifications': data, 'total': len(data)})

@login_required
def marquer_toutes_notifications_lues(request):
    """API pour marquer toutes les notifications comme lues"""
    Notification.objects.filter(
        destinataire=request.user,
        est_lue=False
    ).update(est_lue=True, date_lecture=timezone.now())
    
    return JsonResponse({'success': True, 'message': 'Toutes les notifications marquées comme lues'})

@login_required
def gestion_logs(request):
    """Vue pour la gestion des logs d'actions"""
    if not _require_roles(request, {'SUPER_ADMIN'}):
        return _forbidden(request)
    
    logs = LogAction.objects.select_related('utilisateur').order_by('-date_action')

    q = request.GET.get('q', '').strip()
    action = request.GET.get('action', '').strip()
    user_id = request.GET.get('user_id', '').strip()
    period = request.GET.get('period', '').strip()

    if q:
        logs = logs.filter(
            Q(utilisateur__username__icontains=q) |
            Q(description__icontains=q) |
            Q(modele__icontains=q) |
            Q(adresse_ip__icontains=q)
        )
    if action:
        logs = logs.filter(action=action)
    if user_id:
        logs = logs.filter(utilisateur_id=user_id)

    now = timezone.now()
    if period == 'today':
        logs = logs.filter(date_action__date=now.date())
    elif period == 'week':
        logs = logs.filter(date_action__gte=now - timedelta(days=7))
    elif period == 'month':
        logs = logs.filter(date_action__gte=now - timedelta(days=30))
    elif period == 'year':
        logs = logs.filter(date_action__gte=now - timedelta(days=365))
    
    context = {
        'logs': logs,
        'page_title': 'Logs d\'Actions'
    }
    return render(request, 'dashboard/logs/list.html', context)

# Vues pour modifier et supprimer
@login_required
def modifier_departement(request, departement_id):
    """Vue pour modifier un département"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'DEPARTEMENT_MODIFIER'):
        return _forbidden(request)
    
    departement = get_object_or_404(Departement, id=departement_id)
    
    if request.method == 'POST':
        form = DepartementForm(request.POST, instance=departement)
        if form.is_valid():
            form.save()
            LogAction.objects.create(
                utilisateur=request.user,
                action='MODIFICATION',
                modele='Departement',
                id_objet=departement.id,
                description=f'Modification du département {departement.nom}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('gestion_departements')
    else:
        form = DepartementForm(instance=departement)
    
    context = {
        'form': form,
        'departement': departement,
        'page_title': f'Modifier {departement.nom}'
    }
    return render(request, 'dashboard/departements/form.html', context)

@login_required
def supprimer_departement(request, departement_id):
    """Vue pour supprimer un département"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'DEPARTEMENT_SUPPRIMER'):
        return _forbidden(request)
    
    departement = get_object_or_404(Departement, id=departement_id)
    
    if request.method == 'POST':
        nom = departement.nom
        departement.delete()
        
        LogAction.objects.create(
            utilisateur=request.user,
            action='SUPPRESSION',
            modele='Departement',
            id_objet=departement_id,
            description=f'Suppression du département {nom}',
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'message': f'Département {nom} supprimé avec succès'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def modifier_projet(request, projet_id):
    """Vue pour modifier un projet"""
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not _require_roles(request, {'CHEF_PROJET', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not (request.user.is_super_admin() or request.user.is_admin() or projet.chef_projet == request.user):
        return _forbidden(request)
    if request.user.is_admin() and not _user_has_any_permission(request.user, 'PROJET_MODIFIER'):
        return _forbidden(request)
    
    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            
            # Mettre à jour l'équipe si spécifiée
            if 'equipe' in request.POST:
                projet.equipe.set(request.POST.getlist('equipe'))
            
            LogAction.objects.create(
                utilisateur=request.user,
                action='MODIFICATION',
                modele='Projet',
                id_objet=projet.id,
                description=f'Modification du projet {projet.nom}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('detail_projet', projet_id=projet.id)
    else:
        form = ProjetForm(instance=projet)
    
    context = {
        'form': form,
        'projet': projet,
        'page_title': f'Modifier {projet.nom}'
    }
    return render(request, 'dashboard/projets/form.html', context)

@login_required
def supprimer_projet(request, projet_id):
    """Vue pour supprimer un projet"""
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not _user_has_any_permission(request.user, 'PROJET_SUPPRIMER'):
        return _forbidden(request)
    
    if request.method == 'POST':
        nom = projet.nom
        projet.delete()
        
        LogAction.objects.create(
            utilisateur=request.user,
            action='SUPPRESSION',
            modele='Projet',
            id_objet=projet_id,
            description=f'Suppression du projet {nom}',
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'message': f'Projet {nom} supprimé avec succès'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def modifier_tache(request, tache_id):
    """Vue pour modifier une tâche"""
    tache = get_object_or_404(Tache, id=tache_id)
    
    # Vérifier les permissions
    if not _require_roles(request, {'CHEF_PROJET', 'DEVELOPPEUR', 'COLLABORATEUR', 'STAGIAIRE', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if not (request.user.is_super_admin() or request.user.is_admin() or tache.assigne_a == request.user or tache.projet.chef_projet == request.user):
        return _forbidden(request)
    if request.user.is_admin() and not _user_has_any_permission(request.user, 'TACHE_MODIFIER'):
        return _forbidden(request)
    
    if request.method == 'POST':
        form = TacheForm(request.POST, instance=tache)
        if form.is_valid():
            form.save()
            
            LogAction.objects.create(
                utilisateur=request.user,
                action='MODIFICATION',
                modele='Tache',
                id_objet=tache.id,
                description=f'Modification de la tâche {tache.titre}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('gestion_taches')
    else:
        form = TacheForm(instance=tache)
    
    context = {
        'form': form,
        'tache': tache,
        'page_title': f'Modifier {tache.titre}'
    }
    return render(request, 'dashboard/taches/form.html', context)

@login_required
def supprimer_tache(request, tache_id):
    """Vue pour supprimer une tâche"""
    tache = get_object_or_404(Tache, id=tache_id)
    
    # Vérifier les permissions
    if not (request.user.is_super_admin() or 
              request.user.is_admin() or 
              tache.projet.chef_projet == request.user):
        return redirect('connexion')
    
    if request.method == 'POST':
        titre = tache.titre
        tache.delete()
        
        LogAction.objects.create(
            utilisateur=request.user,
            action='SUPPRESSION',
            modele='Tache',
            id_objet=tache_id,
            description=f'Suppression de la tâche {titre}',
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'message': f'Tâche {titre} supprimée avec succès'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def marquer_tache_terminee(request, tache_id):
    """Vue pour marquer une tâche comme terminée"""
    tache = get_object_or_404(Tache, id=tache_id)
    
    # Vérifier les permissions
    if not (request.user.is_authenticated and 
              (tache.assigne_a == request.user or 
               tache.projet.chef_projet == request.user or
               request.user.is_admin() or 
               request.user.is_super_admin())):
        return redirect('connexion')
    
    if request.method == 'POST':
        tache.statut = 'TERMINE'
        tache.date_terminee = timezone.now()
        tache.progression = 100
        tache.save()
        
        LogAction.objects.create(
            utilisateur=request.user,
            action='MODIFICATION',
            modele='Tache',
            id_objet=tache.id,
            description=f'Tâche {tache.titre} marquée comme terminée',
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'message': 'Tâche marquée comme terminée'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def modifier_utilisateur(request, user_id):
    """Vue pour modifier un utilisateur"""
    if not request.user.can_access_admin_dashboard():
        return redirect('connexion')
    
    # Empêcher la modification des Super Admins par les Admins normaux
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    if not request.user.is_super_admin() and utilisateur.is_super_admin():
        return redirect('connexion')
    
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            
            LogAction.objects.create(
                utilisateur=request.user,
                action='MODIFICATION',
                modele='CustomUser',
                id_objet=utilisateur.id,
                description=f'Modification de l\'utilisateur {utilisateur.username}',
                adresse_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('gestion_utilisateurs')
    else:
        form = UserAdminForm(instance=utilisateur)
    
    context = {
        'form': form,
        'utilisateur': utilisateur,
        'page_title': f'Modifier {utilisateur.username}'
    }
    return render(request, 'dashboard/utilisateurs/form.html', context)

@login_required
def supprimer_utilisateur(request, user_id):
    """Vue pour supprimer un utilisateur"""
    if not request.user.is_super_admin():
        return redirect('connexion')
    
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    
    # Empêcher la suppression du Super Admin actuel
    if utilisateur.id == request.user.id:
        return JsonResponse({'success': False, 'message': 'Vous ne pouvez pas supprimer votre propre compte'})
    
    if request.method == 'POST':
        username = utilisateur.username
        utilisateur.delete()

        LogAction.objects.create(
            utilisateur=request.user,
            action='SUPPRESSION',
            modele='CustomUser',
            id_objet=user_id,
            description=f'Suppression de l\'utilisateur {username}',
            adresse_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Utilisateur {username} supprimé avec succès'})

        messages.success(request, f"Utilisateur {username} supprimé avec succès")
        return redirect('super_admin_manage_users')

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def exporter_logs(request):
    """Vue pour exporter les logs d'actions"""
    if not request.user.can_access_super_admin_dashboard():
        return redirect('connexion')
    
    import csv
    from django.http import HttpResponse
    
    logs = LogAction.objects.select_related('utilisateur').order_by('-date_action')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Utilisateur', 'Action', 'Modèle', 'ID Objet', 'Description', 'Adresse IP'])
    
    for log in logs:
        writer.writerow([
            log.date_action.strftime('%Y-%m-%d %H:%M:%S'),
            log.utilisateur.username,
            log.action,
            log.modele,
            log.id_objet,
            log.description,
            log.adresse_ip
        ])
    
    return response

@login_required
def client_dashboard(request):
    """Tableau de bord pour les clients"""
    if not _require_roles(request, {'CLIENT', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    context = {
        'user_role': 'CLIENT',
        'page_title': 'Tableau de Bord Client'
    }
    return render(request, 'dashboard/client/dashboard.html', context)

@login_required
def collaborateur_dashboard(request):
    """Tableau de bord pour les collaborateurs"""
    if not _require_roles(request, {'COLLABORATEUR', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    context = {
        'user_role': 'COLLABORATEUR',
        'page_title': 'Tableau de Bord Collaborateur'
    }
    return render(request, 'dashboard/collaborateur/dashboard.html', context)

@login_required
def stagiaire_dashboard(request):
    """Tableau de bord pour les stagiaires"""
    if not _require_roles(request, {'STAGIAIRE', 'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    context = {
        'user_role': 'STAGIAIRE',
        'page_title': 'Tableau de Bord Stagiaire'
    }
    return render(request, 'dashboard/stagiaire/dashboard.html', context)

# Fin connexion 

@login_required
def indexAdmin(request):
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    return render(request, 'dashboard/super_admin/indexAdmin.html')

@login_required
def administration_dashboard(request):
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
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
    return render(request, 'dashboard/super_admin/dashboard.html', context)

@login_required
def profil(request):
    """Page profil pour utilisateurs sans rôle spécifique ou avec rôle UTILISATEUR"""
    active_role = _get_active_role_from_session(request) or request.user.get_primary_role()
    
    # Redirection vers les dashboards appropriés selon le rôle
    if active_role == 'SUPER_ADMIN':
        return redirect('super_admin_dashboard')
    if active_role == 'ADMINISTRATEUR':
        return redirect('dashboard')
    if active_role in ['CHEF_PROJET', 'DEVELOPPEUR', 'DESIGNER', 'COMMERCIAL', 'COMPTABLE', 'RH', 'SUPPORT']:
        return redirect('employe_dashboard')
    if active_role == 'FORMATEUR':
        return redirect('formateur_dashboard')
    if active_role == 'CLIENT':
        return redirect('client_dashboard')
    if active_role == 'COLLABORATEUR':
        return redirect('collaborateur_dashboard')
    if active_role == 'STAGIAIRE':
        return redirect('stagiaire_dashboard')
    
    # Si l'utilisateur n'a pas de rôle spécifique, afficher son profil standard
    user = request.user
    
    # Récupérer les informations de l'utilisateur
    context = {
        'user': user,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'has_role': active_role is not None and active_role != 'UTILISATEUR',
    }
    
    return render(request, 'dashboard/mon_profil.html', context)

def deconnexion(request):
    logout(request)
    request.session.flush()
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
    
    # Récupérer les informations de contact depuis la BD
    site_contact = SiteContact.get_contact_actif()
    
    return render(request, 'contact.html', {'site_contact': site_contact})

def apropos(request):
    """Vue pour la page À propos avec contenu dynamique depuis la BD"""
    # Récupérer le contenu actif ou créer un par défaut si aucun n'existe
    apropos = Apropos.objects.filter(est_actif=True).first()
    
    if not apropos:
        # Si aucun contenu n'existe, on passe None au template
        # qui utilisera les valeurs par défaut définies dans le template
        apropos = None
    
    return render(request, 'apropos.html', context={"apropos": apropos})

def blog(request):
    return render(request, 'blog.html')

def realisations(request):
    afficher = Realisation.objects.all()
    apropos = Apropos.objects.filter(est_actif=True).first()
    return render(request, 'realisations.html', context={"afficher": afficher, "apropos": apropos})

def cgu(request):
    page_cgu = PageLegale.objects.filter(type_page='CGU', est_active=True).first()
    return render(request, 'conditionUtilisation.html', {'page': page_cgu})

def politique(request):
    page_politique = PageLegale.objects.filter(type_page='POLITIQUE', est_active=True).first()
    return render(request, "politique.html", {'page': page_politique})

def faq(request):
    faqs = FAQ.objects.filter(est_active=True).order_by('ordre_affichage')
    return render(request, "faq.html", {'faqs': faqs})

def formation(request):
    return render(request, "formation.html")

def service(request):
    service = Services.objects.all()
    return render(request, 'services.html', context={"service":service})

def service_detail(request, slug):
    service = get_object_or_404(Services, slug=slug)
    return render(request, 'service_detail.html', context={"service":service})

# PARTIE ADMINISTRATIVE

# Cette fonction permet d'ajouter les données dans la BD
def AdminApropos(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    if request.method == 'POST':
        form = InsertApropos(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = InsertApropos()
        afficher = Apropos.objects.all()
    return render(request, 'dashboard/super_admin/apropos.html', {'form':form, 'afficher':afficher})

# Cette fonction permet de modifier les données de la table Apropos
def UpdateApropos(request, id_apropos):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    edit_apropos = Apropos.objects.get(id=id_apropos)
    if request.method == 'POST':
        edit_apropos.nom = request.POST.get('nom')
        edit_apropos.contenus = request.POST.get('contenus')
        edit_apropos.save()
        messages.success(request, "Modification effectuée avec succès !")
        return redirect('AdminApropos')
    else:
        messages.error(request, "Erreur lors de la modification !")
    return render(request, 'dashboard/super_admin/updateApropos.html', {'edit_apropos':edit_apropos})

def AdminTemoignage(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    return render(request, 'dashboard/super_admin/temoignage.html')

# ==============================================================================

# Cette fonction permet d'inserer ET D'AFFICHER      
def AdminService(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
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
    return render(request, 'dashboard/super_admin/service.html', {'afficherService':afficherService})


def AdminRealisation(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
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
    return render(request, 'dashboard/super_admin/realisation.html', {'afficherRealisation':afficherRealisation})

def AdminContact(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    afficherMessage = Contact.objects.all()
    return render(request, 'dashboard/super_admin/contact.html', {'afficherMessage':afficherMessage})


# Cette fonction permet de modifier

def EditService(request, pk):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    edit = Services.objects.get(id=pk)

    if request.method == 'POST':
        if len(request.FILES) != 0:
            edit.photo = request.FILES['image']
        edit.nom = request.POST.get('nom')
        edit.description = request.POST.get('description')
        edit.save()
        messages.success(request, "Modification effectuée avec succès !")
        return redirect('AdminService')
    return render(request, 'dashboard/super_admin/edit_service.html', {'edit':edit})

def DeleteService(request, pk):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    delete = Services.objects.get(id=pk)
    if getattr(delete, 'photo', None):
        try:
            delete.photo.delete(save=False)
        except Exception:
            pass
    delete.delete()
    messages.success(request, "Suppression effectuée avec succès !")
    return redirect('AdminService')

def EditRealisation(request, pk):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    edit = Realisation.objects.get(id=pk)

    if request.method == 'POST':
        if len(request.FILES) != 0:
            edit.image = request.FILES['image']
        edit.titre = request.POST.get('nom')
        edit.description = request.POST.get('description')
        edit.save()
        messages.success(request, "Modification effectuée avec succès !")
        return redirect('AdminRealisation')
    return render(request, 'dashboard/super_admin/edit_realisation.html', {'edit':edit})

def DeleteRealisation(request, pk):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    delete = Realisation.objects.get(id=pk)
    if getattr(delete, 'image', None):
        try:
            delete.image.delete(save=False)
        except Exception:
            pass
    delete.delete()
    messages.success(request, "Suppression effectuée avec succès !")
    return redirect('AdminRealisation')

def AdminPartenaire(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    return render(request, 'dashboard/super_admin/partenaire.html')

def AdminFormation(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    form = FormationForm()
    if request.method == "POST":
        form = FormationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('AdminFormation')
    return render(request, 'dashboard/super_admin/formation.html', {'form':form})

def AdminBlog(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    return render(request, 'dashboard/super_admin/blog.html')

def AdminFaq(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    return render(request, 'dashboard/super_admin/faq.html')

# FACTURATION
@login_required
def FacturationView(request):
    """Vue principale pour la facturation"""
    if Devis is None or Facture is None:
        messages.error(request, "Module facturation indisponible (modèles manquants).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/facturation/index_facturation.html', {
        'stats': stats,
        'devis_recents': devis_recents,
        'factures_recentes': factures_recentes,
    })

@login_required
def ListeDevisView(request):
    """Vue pour la liste des devis"""
    if Devis is None:
        messages.error(request, "Module devis indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/facturation/liste_devis.html', {
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
    if Devis is None:
        messages.error(request, "Module devis indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/facturation/ajouter_devis.html', {
        'clients': Client.objects.all(),
        'projets': Projet.objects.all(),
    })

@login_required
def FicheDevisView(request, devis_id):
    """Vue pour la fiche détaillée d'un devis"""
    if Devis is None:
        messages.error(request, "Module devis indisponible (modèle manquant).")
        return redirect('dashboard')
    devis = get_object_or_404(Devis, id=devis_id)
    
    # Vérifier si le devis peut être converti en facture
    peut_convertir = devis.statut == 'ACCEPTE' and not hasattr(devis, 'facture')
    
    return render(request, 'dashboard/super_admin/facturation/fiche_devis.html', {
        'devis': devis,
        'peut_convertir': peut_convertir,
    })

@login_required
def ConvertirDevisFactureView(request, devis_id):
    """Vue pour convertir un devis en facture"""
    if Devis is None or Facture is None:
        messages.error(request, "Module facturation indisponible (modèles manquants).")
        return redirect('dashboard')
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
    if Facture is None:
        messages.error(request, "Module factures indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/facturation/liste_factures.html', {
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
    if Facture is None:
        messages.error(request, "Module factures indisponible (modèle manquant).")
        return redirect('dashboard')
    facture = get_object_or_404(Facture, id=facture_id)
    lignes = facture.lignes.all()
    
    return render(request, 'dashboard/super_admin/facturation/fiche_facture.html', {
        'facture': facture,
        'lignes': lignes,
    })

@login_required
def ExportPDFView(request, facture_id):
    """Vue pour exporter une facture en PDF (MVP - simple redirection)"""
    if Facture is None:
        messages.error(request, "Module factures indisponible (modèle manquant).")
        return redirect('dashboard')
    facture = get_object_or_404(Facture, id=facture_id)
    messages.info(request, f"Fonction PDF à implémenter pour la facture {facture.numero}")
    return redirect('fiche_facture', facture_id=facture_id)

# COLLABORATEURS
@login_required
def ListeCollaborateursView(request):
    """Vue pour la liste des collaborateurs"""
    if Collaborateur is None:
        messages.error(request, "Module collaborateurs indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/collaborateurs/liste_collaborateurs.html', {
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
    if Collaborateur is None:
        messages.error(request, "Module collaborateurs indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/collaborateurs/ajouter_collaborateur.html', {
        'poste_choices': Collaborateur.POSTE_CHOICES,
        'dispo_choices': Collaborateur.DISPO_CHOICES,
        'users': User.objects.all(),
    })

@login_required
def FicheCollaborateurView(request, collaborateur_id):
    """Vue pour la fiche détaillée d'un collaborateur"""
    if Collaborateur is None:
        messages.error(request, "Module collaborateurs indisponible (modèle manquant).")
        return redirect('dashboard')
    collaborateur = get_object_or_404(Collaborateur, id=collaborateur_id)
    
    # Projets actifs
    projets_actifs = collaborateur.user.affectations_projet.filter(est_actif=True).select_related('projet')
    
    # Temps saisi récent
    temps_recent = collaborateur.user.temps_saisi.order_by('-date_saisie')[:10]
    
    # Statistiques
    stats = {
        'total_projets': collaborateur.user.affectations_projet.count(),
        'projets_actifs': projets_actifs.count(),
        'total_heures': collaborateur.user.temps_saisi.aggregate(total=Sum('heures'))['total'] or 0,
        'montant_total': collaborateur.user.temps_saisi.aggregate(total=Sum('montant'))['total'] or 0,
    }
    
    return render(request, 'dashboard/super_admin/collaborateurs/fiche_collaborateur.html', {
        'collaborateur': collaborateur,
        'projets_actifs': projets_actifs,
        'temps_recent': temps_recent,
        'stats': stats,
    })

@login_required
def ModifierCollaborateurView(request, collaborateur_id):
    """Vue pour modifier un collaborateur"""
    if Collaborateur is None:
        messages.error(request, "Module collaborateurs indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/collaborateurs/modifier_collaborateur.html', {
        'collaborateur': collaborateur,
        'poste_choices': Collaborateur.POSTE_CHOICES,
        'dispo_choices': Collaborateur.DISPO_CHOICES,
    })

# SUPPORT CLIENT
@login_required
def SupportView(request):
    """Vue principale pour le support client"""
    if TicketSupport is None:
        messages.error(request, "Module support indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/support/index_support.html', {
        'stats': stats,
        'tickets_recents': tickets_recents,
    })

@login_required
def ListeTicketsView(request):
    """Vue pour la liste des tickets"""
    if TicketSupport is None:
        messages.error(request, "Module support indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/support/liste_tickets.html', {
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
    if TicketSupport is None:
        messages.error(request, "Module support indisponible (modèle manquant).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/support/ajouter_ticket.html', {
        'type_choices': TicketSupport.TYPE_CHOICES,
        'priorite_choices': TicketSupport.PRIORITE_CHOICES,
        'clients': Client.objects.all(),
        'projets': Projet.objects.all(),
    })

@login_required
def FicheTicketView(request, ticket_id):
    """Vue pour la fiche détaillée d'un ticket"""
    if TicketSupport is None or MessageTicket is None:
        messages.error(request, "Module support indisponible (modèles manquants).")
        return redirect('dashboard')
    ticket = get_object_or_404(TicketSupport, id=ticket_id)
    ticket_messages = ticket.messages.select_related('auteur').order_by('date_message')
    
    return render(request, 'dashboard/super_admin/support/fiche_ticket.html', {
        'ticket': ticket,
        'messages': ticket_messages,
    })

@login_required
def AssignerTicketView(request, ticket_id):
    """Vue pour assigner un ticket"""
    if TicketSupport is None or MessageTicket is None:
        messages.error(request, "Module support indisponible (modèles manquants).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/support/assigner_ticket.html', {
        'ticket': ticket,
        'collaborateurs': User.objects.all(),
    })

@login_required
def ResoudreTicketView(request, ticket_id):
    """Vue pour résoudre un ticket"""
    if TicketSupport is None or MessageTicket is None:
        messages.error(request, "Module support indisponible (modèles manquants).")
        return redirect('dashboard')
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
    
    return render(request, 'dashboard/super_admin/support/resoudre_ticket.html', {
        'ticket': ticket,
    })

@login_required
def AjouterMessageView(request, ticket_id):
    """Vue pour ajouter un message à un ticket"""
    if TicketSupport is None or MessageTicket is None:
        messages.error(request, "Module support indisponible (modèles manquants).")
        return redirect('dashboard')
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
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    return render(request, 'dashboard/super_admin/indexAdmin.html')

@login_required
def TempsView(request):
    """Vue pour la gestion du temps"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    return render(request, 'dashboard/super_admin/suivi_temps.html')

@login_required
def ClientsView(request):
    """Vue pour la liste des clients avec pagination, filtres et statistiques"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    search = request.GET.get('search', '')
    statut_filter = request.GET.get('statut_client', '')
    type_filter = request.GET.get('type_client', '')
    
    clients = Client.objects.all().order_by('-date_creation')
    
    # Application des filtres
    if search:
        clients = clients.filter(
            Q(nom__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search) |
            Q(societe__icontains=search)
        )
    
    if statut_filter:
        clients = clients.filter(statut_client=statut_filter)
    
    if type_filter:
        clients = clients.filter(type_client=type_filter)
    
    # Statistiques
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(statut_client='ACTIF').count()
    new_clients_month = Client.objects.filter(
        date_creation__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    total_projects = Projet.objects.count()
    
    # Pagination - 15 clients par page
    paginator = Paginator(clients, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    # Conserver les paramètres de filtre pour la pagination
    query_params = []
    if search:
        query_params.append(f'search={search}')
    if statut_filter:
        query_params.append(f'statut_client={statut_filter}')
    if type_filter:
        query_params.append(f'type_client={type_filter}')
    querystring = '&'.join(query_params)
    
    return render(request, 'dashboard/super_admin/liste_clients.html', {
        'clients': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_clients': total_clients,
        'active_clients': active_clients,
        'new_clients_month': new_clients_month,
        'total_projects': total_projects,
        'search': search,
        'statut_filter': statut_filter,
        'type_filter': type_filter,
        'statut_choices': Client.STATUT_CLIENT_CHOICES,
        'type_choices': Client.TYPE_CLIENT_CHOICES,
        'querystring': querystring,
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
                site_web=request.POST.get('site_web', ''),
                secteur_activite=request.POST.get('secteur_activite', ''),
                notes=request.POST.get('notes', ''),
            )
            client.save()
            messages.success(request, f"Client {client.nom} ajouté avec succès!")
            return redirect('clients')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/super_admin/ajouter_client.html')

@login_required
def FicheClientView(request, client_id):
    """Vue pour la fiche détaillée d'un client"""
    client = get_object_or_404(Client, id=client_id)
    
    # Projets associés (le champ Projet.client est un CharField)
    projets = Projet.objects.filter(client__iexact=client.nom).select_related('chef_projet', 'departement').prefetch_related('equipe').order_by('-date_creation')
    
    # Devis associés - filtrer par email du client car Devis.client est ForeignKey vers CustomUser
    devis = []
    if Devis is not None:
        # Chercher les devis où le client correspond par email ou nom
        devis = Devis.objects.filter(
            Q(client__email=client.email) | 
            Q(client__last_name__icontains=client.nom)
        ).order_by('-date_creation') if client.email else []
    
    # Factures associées
    factures = []
    if Facture is not None:
        factures = Facture.objects.filter(
            Q(client__email=client.email) |
            Q(client__last_name__icontains=client.nom)
        ).order_by('-date_creation') if client.email else []
    
    # Tickets support
    tickets = []
    if TicketSupport is not None:
        tickets = TicketSupport.objects.filter(
            Q(client__email=client.email) |
            Q(client__last_name__icontains=client.nom)
        ).order_by('-date_creation') if client.email else []
    
    # Statistiques
    stats = {
        'total_projets': projets.count(),
        'projets_actifs': projets.filter(statut='EN_COURS').count(),
        'total_devis': len(devis) if isinstance(devis, list) else devis.count(),
        'total_factures': len(factures) if isinstance(factures, list) else factures.count(),
        'factures_impayees': factures.filter(statut='ENVOYEE').count() if Facture is not None and not isinstance(factures, list) else 0,
        'total_tickets': len(tickets) if isinstance(tickets, list) else tickets.count(),
        'tickets_ouverts': tickets.filter(statut='OUVERT').count() if TicketSupport is not None and not isinstance(tickets, list) else 0,
        'chiffre_affaires': (
            factures.filter(statut='PAYEE').aggregate(total=Sum('montant_ttc'))['total'] or 0
        ) if Facture is not None and not isinstance(factures, list) else 0,
    }
    
    return render(request, 'dashboard/super_admin/fiche_client.html', {
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
    
    return render(request, 'dashboard/super_admin/modifier_client.html', {'client': client})

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
    
    return render(request, 'dashboard/super_admin/supprimer_client.html', {'client': client})


@login_required
def export_client_pdf(request, client_id):
    """Vue pour exporter la fiche client en PDF"""
    from django.template.loader import render_to_string
    from django.utils import timezone
    
    client = get_object_or_404(Client, id=client_id)
    
    # Récupérer les données associées (même logique que FicheClientView)
    projets = Projet.objects.filter(client__iexact=client.nom).select_related('chef_projet', 'departement').prefetch_related('equipe').order_by('-date_creation')
    
    # Initialiser devis et factures comme listes vides par défaut
    devis_list = []
    factures_list = []
    
    # Vérifier que Devis est un modèle Django valide (pas NotImplementedType)
    if Devis is not None and type(Devis).__name__ not in ('NotImplementedType', 'NoneType'):
        try:
            if client.email:
                devis_list = list(Devis.objects.filter(
                    Q(client__email=client.email) | 
                    Q(client__last_name__icontains=client.nom)
                ).order_by('-date_creation'))
        except Exception:
            devis_list = []
    
    # Vérifier que Facture est un modèle Django valide
    if Facture is not None and type(Facture).__name__ not in ('NotImplementedType', 'NoneType'):
        try:
            if client.email:
                factures_list = list(Facture.objects.filter(
                    Q(client__email=client.email) |
                    Q(client__last_name__icontains=client.nom)
                ).order_by('-date_creation'))
        except Exception:
            factures_list = []
    
    # Calculer les statistiques
    stats = {
        'total_projets': projets.count(),
        'projets_actifs': projets.filter(statut='EN_COURS').count(),
        'total_devis': len(devis_list),
        'total_factures': len(factures_list),
        'factures_impayees': 0,
        'total_tickets': 0,
        'tickets_ouverts': 0,
        'chiffre_affaires': 0,
    }
    
    # Calculer les factures impayées et chiffre d'affaires si possible
    if factures_list and Facture is not None and type(Facture).__name__ not in ('NotImplementedType', 'NoneType'):
        try:
            stats['factures_impayees'] = sum(1 for f in factures_list if getattr(f, 'statut', None) == 'ENVOYEE')
            stats['chiffre_affaires'] = sum(getattr(f, 'montant_ttc', 0) or 0 for f in factures_list if getattr(f, 'statut', None) == 'PAYEE')
        except Exception:
            pass
    
    # Préparer l'URL du logo pour xhtml2pdf (besoin de chemin absolu)
    from django.contrib.staticfiles.storage import staticfiles_storage
    logo_url = request.build_absolute_uri(staticfiles_storage.url('images/Mupenda Company.png'))
    
    context = {
        'client': client,
        'projets': projets,
        'devis': devis_list,
        'factures': factures_list,
        'stats': stats,
        'now': timezone.now(),
        'logo_url': logo_url,
    }
    
    # Utiliser xhtml2pdf pour générer le PDF
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        
        html_string = render_to_string('dashboard/super_admin/client_pdf.html', context, request)
        
        # Créer le PDF en mémoire
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode('UTF-8')), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="fiche_client_{client.nom}.pdf"'
            return response
        else:
            messages.warning(request, 'Erreur lors de la génération du PDF. Affichage de l\'aperçu HTML.')
            return render(request, 'dashboard/super_admin/client_pdf.html', context)
        
    except Exception as e:
        # En cas d'erreur, afficher l'aperçu HTML
        messages.warning(request, f'Erreur PDF: {str(e)[:100]}. Affichage de l\'aperçu HTML.')
        return render(request, 'dashboard/super_admin/client_pdf.html', context)

@login_required
def liste_equipements(request):
    """Vue pour la liste des équipements"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN', 'CHEF_PROJET'}):
        return _forbidden(request)
    
    search = request.GET.get('search', '')
    marque_filter = request.GET.get('marque', '')
    
    from .models import Equipement
    equipements = Equipement.objects.all().order_by('-created_on')
    
    if search:
        equipements = equipements.filter(
            Q(name__icontains=search) |
            Q(model__icontains=search) |
            Q(marque__icontains=search)
        )
    
    if marque_filter:
        equipements = equipements.filter(marque=marque_filter)
    
    # Pagination
    paginator = Paginator(equipements, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    marques = Equipement.objects.values('marque').distinct().exclude(marque__isnull=True).exclude(marque='')
    
    context = {
        'equipements': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_equipements': Equipement.objects.count(),
        'marques': marques,
        'search': search,
        'marque_filter': marque_filter,
    }
    return render(request, 'dashboard/equipements/liste_equipements.html', context)


@login_required
def creer_equipement(request):
    """Vue pour créer un équipement"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    if request.method == 'POST':
        try:
            from .models import Equipement
            equipement = Equipement(
                name=request.POST.get('name'),
                model=request.POST.get('model'),
                marque=request.POST.get('marque'),
                color=request.POST.get('color', '#000000'),
                quantity=request.POST.get('quantity', 0),
                autres_details=request.POST.get('autres_details', ''),
                author=request.user,
            )
            if request.FILES.get('image'):
                equipement.image = request.FILES.get('image')
            equipement.save()
            messages.success(request, f"Équipement '{equipement.name}' créé avec succès!")
            return redirect('liste_equipements')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/equipements/creer_equipement.html')


@login_required
def modifier_equipement(request, pk):
    """Vue pour modifier un équipement"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    from .models import Equipement
    equipement = get_object_or_404(Equipement, slug=pk)
    
    if request.method == 'POST':
        try:
            equipement.name = request.POST.get('name')
            equipement.model = request.POST.get('model')
            equipement.marque = request.POST.get('marque')
            equipement.color = request.POST.get('color', '#000000')
            equipement.quantity = request.POST.get('quantity', 0)
            equipement.autres_details = request.POST.get('autres_details', '')
            if request.FILES.get('image'):
                equipement.image = request.FILES.get('image')
            equipement.save()
            messages.success(request, f"Équipement '{equipement.name}' modifié avec succès!")
            return redirect('liste_equipements')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/equipements/modifier_equipement.html', {'equipement': equipement})


@login_required
def supprimer_equipement(request, pk):
    """Vue pour supprimer un équipement"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    from .models import Equipement
    equipement = get_object_or_404(Equipement, slug=pk)
    
    if request.method == 'POST':
        try:
            nom = equipement.name
            equipement.delete()
            messages.success(request, f"Équipement '{nom}' supprimé avec succès!")
            return redirect('liste_equipements')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/equipements/supprimer_equipement.html', {'equipement': equipement})


# =============================================================================
# VUES CRUD POUR FORMATEUR
# =============================================================================

@login_required
def liste_formateurs(request):
    """Vue pour la liste des formateurs"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN', 'FORMATEUR'}):
        return _forbidden(request)
    
    search = request.GET.get('search', '')
    sexe_filter = request.GET.get('sexe', '')
    
    from .models import Formateur
    formateurs = Formateur.objects.all().order_by('-created_on')
    
    if search:
        formateurs = formateurs.filter(
            Q(nom__icontains=search) |
            Q(postnom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email__icontains=search) |
            Q(specialite__icontains=search)
        )
    
    if sexe_filter:
        formateurs = formateurs.filter(sexe=sexe_filter)
    
    # Pagination
    paginator = Paginator(formateurs, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'formateurs': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_formateurs': Formateur.objects.count(),
        'search': search,
        'sexe_filter': sexe_filter,
        'sexe_choices': Formateur.SEX_CHOICES,
    }
    return render(request, 'dashboard/formateurs/liste_formateurs.html', context)


@login_required
def creer_formateur(request):
    """Vue pour créer un formateur"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    if request.method == 'POST':
        try:
            from .models import Formateur
            formateur = Formateur(
                nom=request.POST.get('nom'),
                postnom=request.POST.get('postnom'),
                prenom=request.POST.get('prenom'),
                sexe=request.POST.get('sexe', 'M'),
                age=request.POST.get('age', 18),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                addresse=request.POST.get('addresse', 'Goma/Nord-Kivu'),
                specialite=request.POST.get('specialite', 'Formateur'),
            )
            if request.FILES.get('image'):
                formateur.image = request.FILES.get('image')
            formateur.save()
            messages.success(request, f"Formateur '{formateur.nom} {formateur.prenom}' créé avec succès!")
            return redirect('liste_formateurs')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    from .models import Formateur
    return render(request, 'dashboard/formateurs/creer_formateur.html', {'sexe_choices': Formateur.SEX_CHOICES})


@login_required
def modifier_formateur(request, pk):
    """Vue pour modifier un formateur"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    from .models import Formateur
    formateur = get_object_or_404(Formateur, pk=pk)
    
    if request.method == 'POST':
        try:
            formateur.nom = request.POST.get('nom')
            formateur.postnom = request.POST.get('postnom')
            formateur.prenom = request.POST.get('prenom')
            formateur.sexe = request.POST.get('sexe', 'M')
            formateur.age = request.POST.get('age', 18)
            formateur.email = request.POST.get('email')
            formateur.phone = request.POST.get('phone')
            formateur.addresse = request.POST.get('addresse', 'Goma/Nord-Kivu')
            formateur.specialite = request.POST.get('specialite', 'Formateur')
            if request.FILES.get('image'):
                formateur.image = request.FILES.get('image')
            formateur.save()
            messages.success(request, f"Formateur '{formateur.nom} {formateur.prenom}' modifié avec succès!")
            return redirect('liste_formateurs')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/formateurs/modifier_formateur.html', {
        'formateur': formateur,
        'sexe_choices': Formateur.SEX_CHOICES
    })


@login_required
def supprimer_formateur(request, pk):
    """Vue pour supprimer un formateur"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    from .models import Formateur
    formateur = get_object_or_404(Formateur, pk=pk)
    
    if request.method == 'POST':
        try:
            nom = f"{formateur.nom} {formateur.prenom}"
            formateur.delete()
            messages.success(request, f"Formateur '{nom}' supprimé avec succès!")
            return redirect('liste_formateurs')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/formateurs/supprimer_formateur.html', {'formateur': formateur})


# =============================================================================
# VUES CRUD POUR CATEGORY
# =============================================================================

@login_required
def liste_categories(request):
    """Vue pour la liste des catégories"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    search = request.GET.get('search', '')
    
    categories = Category.objects.all().order_by('name')
    
    if search:
        categories = categories.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(categories, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'categories': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_categories': Category.objects.count(),
        'search': search,
    }
    return render(request, 'dashboard/categories/liste_categories.html', context)


@login_required
def creer_categorie(request):
    """Vue pour créer une catégorie"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    if request.method == 'POST':
        try:
            categorie = Category(
                name=request.POST.get('name'),
            )
            categorie.save()
            messages.success(request, f"Catégorie '{categorie.name}' créée avec succès!")
            return redirect('liste_categories')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/categories/creer_categorie.html')


@login_required
def modifier_categorie(request, pk):
    """Vue pour modifier une catégorie"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    categorie = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        try:
            categorie.name = request.POST.get('name')
            categorie.save()
            messages.success(request, f"Catégorie '{categorie.name}' modifiée avec succès!")
            return redirect('liste_categories')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'dashboard/categories/modifier_categorie.html', {'categorie': categorie})


@login_required
def supprimer_categorie(request, pk):
    """Vue pour supprimer une catégorie"""
    if not _require_roles(request, {'ADMINISTRATEUR', 'SUPER_ADMIN'}):
        return _forbidden(request)
    
    categorie = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        try:
            nom = categorie.name
            categorie.delete()
            messages.success(request, f"Catégorie '{nom}' supprimée avec succès!")
            return redirect('liste_categories')
        except Exception as e:
            messages.error(request, f"Erreur: Cette catégorie est peut-être utilisée par d'autres éléments.")
    
    return render(request, 'dashboard/categories/supprimer_categorie.html', {'categorie': categorie})


def newsletter_subscribe(request):
    """Vue pour l'inscription à la newsletter avec validation email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        # Validation 1: Email non vide
        if not email:
            return JsonResponse({
                'success': False, 
                'message': "Veuillez entrer une adresse email."
            })
        
        # Validation 2: Format email valide
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False, 
                'message': "Veuillez entrer une adresse email valide."
            })
        
        # Validation 3: Domaine email valide (pas de jetable/trash)
        invalid_domains = ['test.com', 'example.com', 'fake.com', 'test.fr']
        domain = email.split('@')[-1]
        if domain in invalid_domains:
            return JsonResponse({
                'success': False, 
                'message': "Ce domaine email n'est pas autorisé."
            })
        
        try:
            # Vérifier si l'email existe déjà
            try:
                subscriber = NewsletterSubscriber.objects.get(email=email)
                # Email existe déjà
                if subscriber.est_actif:
                    return JsonResponse({
                        'success': False, 
                        'message': "Cet email est déjà inscrit à notre newsletter."
                    })
                else:
                    # Réactiver l'abonnement
                    subscriber.est_actif = True
                    subscriber.save()
                    return JsonResponse({
                        'success': True, 
                        'message': "Votre abonnement a été réactivé !"
                    })
            except NewsletterSubscriber.DoesNotExist:
                # Nouvel email - créer l'abonné
                NewsletterSubscriber.objects.create(
                    email=email,
                    ip_inscription=request.META.get('REMOTE_ADDR'),
                    est_actif=True
                )
                return JsonResponse({
                    'success': True, 
                    'message': "Merci pour votre inscription à notre newsletter !"
                })
                    
        except Exception as e:
            import traceback
            print(f"Newsletter error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False, 
                'message': "Une erreur s'est produite. Veuillez réessayer."
            })
    
    # Pour les requêtes GET, rediriger vers la page d'accueil
    return redirect('index')


# ==============================================================================
# VUES MON PROFIL - Utilisateurs sans rôle spécifique
# ==============================================================================

@login_required
def mon_profil_update(request):
    """Mise à jour du profil utilisateur standard"""
    if request.method != 'POST':
        return redirect('profil')
    
    user = request.user
    user.first_name = request.POST.get('first_name', '').strip()
    user.last_name = request.POST.get('last_name', '').strip()
    user.email = request.POST.get('email', '').strip()
    user.telephone = request.POST.get('telephone', '').strip() or None
    
    if request.FILES.get('photo_profil'):
        user.photo_profil = request.FILES.get('photo_profil')
    
    try:
        user.save()
        messages.success(request, 'Vos informations ont été mises à jour avec succès.')
    except Exception as e:
        messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
    
    return redirect('profil')


@login_required
def mon_profil_password(request):
    """Changement de mot de passe pour utilisateur standard"""
    if request.method != 'POST':
        return redirect('profil')
    
    current_password = request.POST.get('current_password', '')
    new_password = request.POST.get('new_password', '')
    confirm_password = request.POST.get('confirm_password', '')
    
    if not request.user.check_password(current_password):
        messages.error(request, 'Mot de passe actuel incorrect.')
        return redirect('profil')
    
    if new_password != confirm_password:
        messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
        return redirect('profil')
    
    if len(new_password) < 8:
        messages.error(request, 'Le nouveau mot de passe doit contenir au moins 8 caractères.')
        return redirect('profil')
    
    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)
    messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
    return redirect('profil')


@login_required
def mon_profil_delete(request):
    """Suppression du compte utilisateur"""
    if request.method != 'POST':
        return redirect('profil')
    
    confirmation = request.POST.get('confirmation', '')
    if confirmation != 'SUPPRIMER':
        messages.error(request, 'Confirmation invalide. Votre compte n\'a pas été supprimé.')
        return redirect('profil')
    
    user = request.user
    username = user.username
    
    # Déconnexion avant suppression
    logout(request)
    request.session.flush()
    
    # Suppression du compte
    user.delete()
    
    messages.success(request, f'Votre compte {username} a été supprimé avec succès.')
    return redirect('index')


@login_required
def mon_profil_message(request):
    """Envoi de message par l'utilisateur"""
    if request.method != 'POST':
        return redirect('profil')
    
    sujet = request.POST.get('sujet', '').strip()
    message_text = request.POST.get('message', '').strip()
    type_demande = request.POST.get('type_demande', 'GENERAL')
    
    if not sujet or not message_text:
        messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
        return redirect('profil')
    
    # Créer un objet Contact (utilisé comme message)
    try:
        contact_msg = Contact(
            nom=request.user.last_name or request.user.username,
            prenom=request.user.first_name or '',
            phone=request.user.telephone or '',
            email=request.user.email,
            message=f"[{type_demande}] {sujet}\n\n{message_text}"
        )
        contact_msg.save()
        messages.success(request, 'Votre message a été envoyé avec succès. Notre équipe vous répondra dans les plus brefs délais.')
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'envoi du message : {str(e)}')
    
    return redirect('profil')


@login_required
def mon_profil_appels_offres(request):
    """Consultation des appels d'offres pour utilisateurs standards"""
    # Essayer de récupérer les appels d'offres depuis la BD
    try:
        from .models import AppelOffre
        appels_offres = AppelOffre.objects.filter(
            est_actif=True, 
            date_limite__gte=timezone.now()
        ).order_by('-date_publication')
    except ImportError:
        # Si le modèle n'existe pas, retourner une liste vide
        appels_offres = []
    
    context = {
        'appels_offres': appels_offres,
    }
    return render(request, 'dashboard/mon_profil_appels_offres.html', context)


@login_required
def mon_profil_devis(request):
    """Création de devis/demande par l'utilisateur"""
    if request.method == 'POST':
        try:
            # Debug: afficher les données reçues
            print("=== DONNÉES POST REÇUES ===")
            print(f"type_demande: {request.POST.get('type_demande')}")
            print(f"description: {request.POST.get('description')}")
            print(f"budget: {request.POST.get('budget')}")
            print(f"delai: {request.POST.get('delai')}")
            print(f"user: {request.user}")
            print("===========================")
            
            # Récupérer les données du formulaire
            type_projet = request.POST.get('type_demande', 'AUTRE').strip()
            description = request.POST.get('description', '').strip()
            budget_text = request.POST.get('budget', '').strip()
            delai_text = request.POST.get('delai', '').strip()
            
            # Validation des champs requis
            if not description:
                messages.error(request, 'La description du projet est requise.')
                return render(request, 'dashboard/mon_profil_devis.html')
            
            # Construire un titre à partir du type
            titre = f"Demande {type_projet.replace('_', ' ').title()}"
            
            # Créer le devis avec le nouveau modèle
            devis = Devis(
                client=request.user,
                titre=titre,
                type_projet=type_projet,
                description=description,
                budget_estime=None,
                date_souhaitee=None,
                statut='EN_ATTENTE'
            )
            devis.save()
            
            print(f"✓ Devis créé avec succès: ID={devis.id}")
            messages.success(request, 'Votre demande de devis a été créée avec succès. Nous vous contacterons prochainement.')
            return redirect('profil')
        except Exception as e:
            import traceback
            print(f"✗ ERREUR lors de la création du devis: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Erreur lors de l\'envoi : {str(e)}')
    
    return render(request, 'dashboard/mon_profil_devis.html')


@login_required
def voir_devis(request, devis_id):
    """Vue pour voir le détail d'un devis"""
    devis = get_object_or_404(Devis, id=devis_id, client=request.user)
    return render(request, 'dashboard/voir_devis.html', {'devis': devis})


@login_required
def annuler_devis(request, devis_id):
    """Vue pour annuler un devis"""
    devis = get_object_or_404(Devis, id=devis_id, client=request.user)
    
    if request.method == 'POST':
        # Vérifier que le devis peut être annulé
        if devis.statut in ['EN_ATTENTE', 'VALIDE']:
            devis.annuler()
            messages.success(request, 'Votre demande de devis a été annulée avec succès.')
        else:
            messages.error(request, 'Ce devis ne peut plus être annulé.')
        return redirect('profil')
    
    return render(request, 'dashboard/annuler_devis.html', {'devis': devis})
