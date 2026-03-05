"""
Template tags pour le menu dashboard dynamique selon le rôle.
"""
from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

register = template.Library()


# Configuration du menu par rôle
MENU_CONFIG = {
    'SUPER_ADMIN': {
        'badge': 'Super Admin',
        'badge_class': 'super-admin-badge',
        'sections': [
            {
                'title': 'Tableau de Bord',
                'icon': 'bi-speedometer2',
                'items': [
                    {'name': 'Dashboard Principal', 'url': 'super_admin_dashboard', 'icon': 'bi-grid-1x2'},
                    {'name': 'Analytics & KPIs', 'url': 'analytics_center', 'icon': 'bi-graph-up'},
                ]
            },
            {
                'title': 'Gestion Utilisateurs',
                'icon': 'bi-people',
                'items': [
                    {'name': 'Utilisateurs', 'url': 'super_admin_manage_users', 'icon': 'bi-people'},
                    {'name': 'Rôles', 'url': 'super_admin_manage_roles', 'icon': 'bi-shield-plus'},
                    {'name': 'Permissions', 'url': 'super_admin_manage_permissions', 'icon': 'bi-key'},
                    {'name': 'Sessions', 'url': 'sessions_management', 'icon': 'bi-clock-history'},
                ]
            },
            {
                'title': 'Sécurité',
                'icon': 'bi-shield-exclamation',
                'items': [
                    {'name': 'Sécurité', 'url': 'security_dashboard', 'icon': 'bi-shield-check'},
                    {'name': 'Logs d\'Audit', 'url': 'audit_logs', 'icon': 'bi-file-text'},
                ]
            },
            {
                'title': 'Administration',
                'icon': 'bi-gear',
                'items': [
                    {'name': 'Maintenance', 'url': 'maintenance_center', 'icon': 'bi-tools'},
                    {'name': 'Notifications', 'url': 'notifications_center', 'icon': 'bi-bell'},
                ]
            },
            {
                'title': 'Gestion Clients',
                'icon': 'bi-briefcase',
                'items': [
                    {'name': 'Clients', 'url': 'clients', 'icon': 'bi-people'},
                    {'name': 'Facturation', 'url': 'facturation', 'icon': 'bi-file-earmark-text'},
                    {'name': 'Support', 'url': 'support', 'icon': 'bi-headset'},
                ]
            },
            {
                'title': 'Projets',
                'icon': 'bi-folder',
                'items': [
                    {'name': 'Projets', 'url': 'AdminProjets', 'icon': 'bi-folder'},
                    {'name': 'Time Tracking', 'url': 'temps', 'icon': 'bi-clock'},
                    {'name': 'Collaborateurs', 'url': 'liste_collaborateurs', 'icon': 'bi-people'},
                ]
            },
            {
                'title': 'Contenu',
                'icon': 'bi-file-earmark',
                'items': [
                    {'name': 'Services', 'url': 'AdminService', 'icon': 'bi-briefcase'},
                    {'name': 'Réalisations', 'url': 'AdminRealisation', 'icon': 'bi-trophy'},
                    {'name': 'Formations', 'url': 'AdminFormation', 'icon': 'bi-mortarboard'},
                    {'name': 'Blog', 'url': 'AdminBlog', 'icon': 'bi-newspaper'},
                ]
            },
            {
                'title': 'Communication',
                'icon': 'bi-envelope',
                'items': [
                    {'name': 'Contacts', 'url': 'AdminContact', 'icon': 'bi-envelope'},
                    {'name': 'FAQ', 'url': 'AdminFaq', 'icon': 'bi-question-circle'},
                    {'name': 'Témoignages', 'url': 'AdminTemoignage', 'icon': 'bi-star'},
                    {'name': 'Partenaires', 'url': 'AdminPartenaire', 'icon': 'bi-handshake'},
                ]
            },
            {
                'title': 'Ressources',
                'icon': 'bi-box-seam',
                'items': [
                    {'name': 'Équipements', 'url': 'liste_equipements', 'icon': 'bi-tools'},
                    {'name': 'Formateurs', 'url': 'liste_formateurs', 'icon': 'bi-person-workspace'},
                    {'name': 'Catégories', 'url': 'liste_categories', 'icon': 'bi-tags'},
                ]
            },
        ]
    },
    'ADMINISTRATEUR': {
        'badge': 'Administrateur',
        'badge_class': 'admin-badge',
        'sections': [
            {
                'title': 'Tableau de Bord',
                'icon': 'bi-speedometer2',
                'items': [
                    {'name': 'Dashboard', 'url': 'dashboard', 'icon': 'bi-grid-1x2'},
                ]
            },
            {
                'title': 'Gestion',
                'icon': 'bi-people',
                'items': [
                    {'name': 'Utilisateurs', 'url': 'gestion_utilisateurs', 'icon': 'bi-people'},
                    {'name': 'Départements', 'url': 'gestion_departements', 'icon': 'bi-building'},
                ]
            },
            {
                'title': 'Projets',
                'icon': 'bi-folder',
                'items': [
                    {'name': 'Projets', 'url': 'gestion_projets', 'icon': 'bi-folder'},
                    {'name': 'Tâches', 'url': 'gestion_taches', 'icon': 'bi-list-check'},
                ]
            },
            {
                'title': 'Contenu',
                'icon': 'bi-file-earmark',
                'items': [
                    {'name': 'Services', 'url': 'AdminService', 'icon': 'bi-briefcase'},
                    {'name': 'Réalisations', 'url': 'AdminRealisation', 'icon': 'bi-trophy'},
                    {'name': 'Formations', 'url': 'AdminFormation', 'icon': 'bi-mortarboard'},
                    {'name': 'Blog', 'url': 'AdminBlog', 'icon': 'bi-newspaper'},
                ]
            },
            {
                'title': 'Communication',
                'icon': 'bi-envelope',
                'items': [
                    {'name': 'Contacts', 'url': 'AdminContact', 'icon': 'bi-envelope'},
                    {'name': 'FAQ', 'url': 'AdminFaq', 'icon': 'bi-question-circle'},
                    {'name': 'Témoignages', 'url': 'AdminTemoignage', 'icon': 'bi-star'},
                ]
            },
        ]
    },
    'CHEF_PROJET': {
        'badge': 'Chef de Projet',
        'badge_class': 'chef-badge',
        'sections': [
            {
                'title': 'Tableau de Bord',
                'icon': 'bi-speedometer2',
                'items': [
                    {'name': 'Dashboard', 'url': 'employe_dashboard', 'icon': 'bi-grid-1x2'},
                ]
            },
            {
                'title': 'Projets',
                'icon': 'bi-folder',
                'items': [
                    {'name': 'Mes Projets', 'url': 'gestion_projets', 'icon': 'bi-folder'},
                    {'name': 'Tâches', 'url': 'gestion_taches', 'icon': 'bi-list-check'},
                    {'name': 'Time Tracking', 'url': 'temps', 'icon': 'bi-clock'},
                ]
            },
            {
                'title': 'Équipe',
                'icon': 'bi-people',
                'items': [
                    {'name': 'Collaborateurs', 'url': 'liste_collaborateurs', 'icon': 'bi-people'},
                ]
            },
        ]
    },
    'DEVELOPPEUR': {
        'badge': 'Développeur',
        'badge_class': 'dev-badge',
        'sections': [
            {
                'title': 'Tableau de Bord',
                'icon': 'bi-speedometer2',
                'items': [
                    {'name': 'Dashboard', 'url': 'employe_dashboard', 'icon': 'bi-grid-1x2'},
                ]
            },
            {
                'title': 'Travail',
                'icon': 'bi-code-square',
                'items': [
                    {'name': 'Mes Tâches', 'url': 'gestion_taches', 'icon': 'bi-list-check'},
                    {'name': 'Time Tracking', 'url': 'temps', 'icon': 'bi-clock'},
                    {'name': 'Projets', 'url': 'gestion_projets', 'icon': 'bi-folder'},
                ]
            },
        ]
    },
    'CLIENT': {
        'badge': 'Client',
        'badge_class': 'client-badge',
        'sections': [
            {
                'title': 'Mon Espace',
                'icon': 'bi-person',
                'items': [
                    {'name': 'Dashboard', 'url': 'client_dashboard', 'icon': 'bi-grid-1x2'},
                    {'name': 'Mes Projets', 'url': 'gestion_projets', 'icon': 'bi-folder'},
                    {'name': 'Support', 'url': 'support', 'icon': 'bi-headset'},
                ]
            },
        ]
    },
    'FORMATEUR': {
        'badge': 'Formateur',
        'badge_class': 'formateur-badge',
        'sections': [
            {
                'title': 'Mon Espace',
                'icon': 'bi-person',
                'items': [
                    {'name': 'Dashboard', 'url': 'formateur_dashboard', 'icon': 'bi-grid-1x2'},
                    {'name': 'Formations', 'url': 'AdminFormation', 'icon': 'bi-mortarboard'},
                ]
            },
        ]
    },
    'COLLABORATEUR': {
        'badge': 'Collaborateur',
        'badge_class': 'collab-badge',
        'sections': [
            {
                'title': 'Tableau de Bord',
                'icon': 'bi-speedometer2',
                'items': [
                    {'name': 'Dashboard', 'url': 'collaborateur_dashboard', 'icon': 'bi-grid-1x2'},
                ]
            },
            {
                'title': 'Travail',
                'icon': 'bi-briefcase',
                'items': [
                    {'name': 'Mes Tâches', 'url': 'gestion_taches', 'icon': 'bi-list-check'},
                    {'name': 'Time Tracking', 'url': 'temps', 'icon': 'bi-clock'},
                ]
            },
        ]
    },
    'STAGIAIRE': {
        'badge': 'Stagiaire',
        'badge_class': 'stagiaire-badge',
        'sections': [
            {
                'title': 'Mon Espace',
                'icon': 'bi-person',
                'items': [
                    {'name': 'Dashboard', 'url': 'stagiaire_dashboard', 'icon': 'bi-grid-1x2'},
                    {'name': 'Mes Tâches', 'url': 'gestion_taches', 'icon': 'bi-list-check'},
                ]
            },
        ]
    },
}


def _get_user_role_context(user, request):
    """Récupère le contexte du menu pour l'utilisateur."""
    # Récupérer le rôle actif depuis la session ou le rôle principal
    active_role = request.session.get('active_role') if request else None
    
    if not active_role and user.is_authenticated:
        active_role = user.get_primary_role()
    
    # Déterminer le rôle à utiliser
    role_key = active_role if active_role in MENU_CONFIG else 'COLLABORATEUR'
    
    # Déterminer le dashboard URL
    dashboard_url = 'connexion'
    if role_key == 'SUPER_ADMIN':
        dashboard_url = 'super_admin_dashboard'
    elif role_key == 'ADMINISTRATEUR':
        dashboard_url = 'dashboard'
    elif role_key == 'CHEF_PROJET':
        dashboard_url = 'employe_dashboard'
    elif role_key == 'DEVELOPPEUR':
        dashboard_url = 'employe_dashboard'
    elif role_key == 'CLIENT':
        dashboard_url = 'client_dashboard'
    elif role_key == 'FORMATEUR':
        dashboard_url = 'formateur_dashboard'
    elif role_key == 'COLLABORATEUR':
        dashboard_url = 'collaborateur_dashboard'
    elif role_key == 'STAGIAIRE':
        dashboard_url = 'stagiaire_dashboard'
    
    menu_data = MENU_CONFIG.get(role_key, MENU_CONFIG['COLLABORATEUR'])
    
    return {
        'role_key': role_key,
        'badge': menu_data['badge'],
        'badge_class': menu_data['badge_class'],
        'sections': menu_data['sections'],
        'dashboard_url': dashboard_url,
        'active_role': active_role,
    }


@register.inclusion_tag('dashboard/partials/_sidebar_menu.html', takes_context=True)
def render_sidebar_menu(context):
    """
    Rend le menu sidebar dynamique selon le rôle de l'utilisateur.
    Usage: {% load dashboard_menu %}{% render_sidebar_menu %}
    """
    request = context.get('request')
    user = context.get('user')
    
    if not user or not user.is_authenticated:
        return {'sections': [], 'badge': 'Invité', 'badge_class': ''}
    
    menu_context = _get_user_role_context(user, request)
    
    # Résoudre les URLs et marquer l'actif
    current_url_name = request.resolver_match.url_name if request and hasattr(request, 'resolver_match') else None
    
    for section in menu_context['sections']:
        for item in section['items']:
            try:
                item['resolved_url'] = reverse(item['url'])
                item['is_active'] = (item['url'] == current_url_name)
            except NoReverseMatch:
                item['resolved_url'] = '#'
                item['is_active'] = False
    
    return menu_context


@register.simple_tag(takes_context=True)
def get_user_badge_info(context):
    """
    Retourne les informations du badge utilisateur.
    Usage: {% load dashboard_menu %}{% get_user_badge_info as badge_info %}
    """
    request = context.get('request')
    user = context.get('user')
    
    if not user or not user.is_authenticated:
        return {'badge': 'Invité', 'badge_class': '', 'role_key': None}
    
    menu_context = _get_user_role_context(user, request)
    return {
        'badge': menu_context['badge'],
        'badge_class': menu_context['badge_class'],
        'role_key': menu_context['role_key'],
    }


@register.simple_tag(takes_context=True)
def get_dashboard_home_url(context):
    """
    Retourne l'URL du dashboard selon le rôle.
    Usage: {% load dashboard_menu %}{% get_dashboard_home_url as home_url %}
    """
    request = context.get('request')
    user = context.get('user')
    
    if not user or not user.is_authenticated:
        return reverse('connexion')
    
    menu_context = _get_user_role_context(user, request)
    try:
        return reverse(menu_context['dashboard_url'])
    except NoReverseMatch:
        return reverse('connexion')


@register.filter
def has_permission_access(user, permission_code):
    """
    Vérifie si l'utilisateur a accès à une permission spécifique.
    Usage: {% if user|has_permission_access:'VIEW_USERS' %}
    """
    if not user or not user.is_authenticated:
        return False
    return user.has_permission(permission_code)


@register.filter
def has_role_access(user, role_names):
    """
    Vérifie si l'utilisateur a l'un des rôles spécifiés.
    Usage: {% if user|has_role_access:'SUPER_ADMIN,ADMINISTRATEUR' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    roles = [r.strip() for r in role_names.split(',')]
    user_roles = [ur.role.nom for ur in user.user_roles.filter(est_actif=True)]
    
    return any(role in user_roles for role in roles)
