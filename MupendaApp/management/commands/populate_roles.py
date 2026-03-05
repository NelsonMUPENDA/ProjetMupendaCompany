# Script de peuplement initial des rôles et permissions
from django.core.management.base import BaseCommand
from django.utils import timezone
from MupendaApp.models import Role, Permission, CustomUser, UserRole

class Command(BaseCommand):
    help = 'Peuple la base de données avec les rôles et permissions par défaut'

    def handle(self, *args, **options):
        self.stdout.write('Création des permissions par défaut...')
        
        # Création des permissions par catégorie
        permissions_data = [
            # Gestion des utilisateurs
            ('USER_CREATE', 'Créer des utilisateurs', 'UTILISATEUR'),
            ('USER_READ', 'Voir les utilisateurs', 'UTILISATEUR'),
            ('USER_UPDATE', 'Modifier les utilisateurs', 'UTILISATEUR'),
            ('USER_DELETE', 'Supprimer les utilisateurs', 'UTILISATEUR'),
            ('USER_BAN', 'Bannir des utilisateurs', 'UTILISATEUR'),
            
            # Gestion des rôles
            ('ROLE_CREATE', 'Créer des rôles', 'ROLE'),
            ('ROLE_READ', 'Voir les rôles', 'ROLE'),
            ('ROLE_UPDATE', 'Modifier les rôles', 'ROLE'),
            ('ROLE_DELETE', 'Supprimer les rôles', 'ROLE'),
            ('ROLE_ASSIGN', 'Attribuer des rôles', 'ROLE'),
            
            # Gestion des projets
            ('PROJECT_CREATE', 'Créer des projets', 'PROJET'),
            ('PROJECT_READ', 'Voir les projets', 'PROJET'),
            ('PROJECT_UPDATE', 'Modifier les projets', 'PROJET'),
            ('PROJECT_DELETE', 'Supprimer les projets', 'PROJET'),
            ('PROJECT_ASSIGN', 'Assigner des projets', 'PROJET'),
            
            # Gestion des clients
            ('CLIENT_CREATE', 'Créer des clients', 'CLIENT'),
            ('CLIENT_READ', 'Voir les clients', 'CLIENT'),
            ('CLIENT_UPDATE', 'Modifier les clients', 'CLIENT'),
            ('CLIENT_DELETE', 'Supprimer des clients', 'CLIENT'),
            
            # Gestion de la facturation
            ('INVOICE_CREATE', 'Créer des factures', 'FACTURATION'),
            ('INVOICE_READ', 'Voir les factures', 'FACTURATION'),
            ('INVOICE_UPDATE', 'Modifier les factures', 'FACTURATION'),
            ('INVOICE_DELETE', 'Supprimer les factures', 'FACTURATION'),
            ('INVOICE_VALIDATE', 'Valider les factures', 'FACTURATION'),
            
            # Gestion du contenu
            ('CONTENT_CREATE', 'Créer du contenu', 'CONTENU'),
            ('CONTENT_READ', 'Voir le contenu', 'CONTENU'),
            ('CONTENT_UPDATE', 'Modifier le contenu', 'CONTENU'),
            ('CONTENT_DELETE', 'Supprimer le contenu', 'CONTENU'),
            ('CONTENT_PUBLISH', 'Publier du contenu', 'CONTENU'),
            
            # Accès aux rapports
            ('REPORT_VIEW', 'Voir les rapports', 'RAPPORT'),
            ('REPORT_EXPORT', 'Exporter des rapports', 'RAPPORT'),
            ('REPORT_ANALYTICS', 'Voir les analytics', 'RAPPORT'),
            
            # Administration système
            ('SYSTEM_CONFIG', 'Configurer le système', 'SYSTEME'),
            ('SYSTEM_BACKUP', 'Effectuer des backups', 'SYSTEME'),
            ('SYSTEM_LOGS', 'Voir les logs système', 'SYSTEME'),
            ('SYSTEM_MONITOR', 'Monitorer le système', 'SYSTEME'),
            
            # Gestion du support
            ('SUPPORT_CREATE', 'Créer des tickets', 'SUPPORT'),
            ('SUPPORT_READ', 'Voir les tickets', 'SUPPORT'),
            ('SUPPORT_UPDATE', 'Modifier les tickets', 'SUPPORT'),
            ('SUPPORT_DELETE', 'Supprimer les tickets', 'SUPPORT'),
            ('SUPPORT_ASSIGN', 'Assigner des tickets', 'SUPPORT'),
            
            # Gestion des formations
            ('FORMATION_CREATE', 'Créer des formations', 'FORMATION'),
            ('FORMATION_READ', 'Voir les formations', 'FORMATION'),
            ('FORMATION_UPDATE', 'Modifier les formations', 'FORMATION'),
            ('FORMATION_DELETE', 'Supprimer les formations', 'FORMATION'),
            ('FORMATION_TEACH', 'Enseigner des formations', 'FORMATION'),
        ]
        
        created_permissions = []
        for code, nom, categorie in permissions_data:
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'nom': nom,
                    'categorie': categorie,
                    'est_active': True
                }
            )
            if created:
                created_permissions.append(permission)
                self.stdout.write(f'  ✓ Permission créée: {nom}')
        
        self.stdout.write(f'\n{len(created_permissions)} permissions créées avec succès!')
        
        # Création des rôles avec leurs permissions
        self.stdout.write('\nCréation des rôles par défaut...')
        
        roles_data = [
            ('SUPER_ADMIN', 'Super Administrateur', 10, [
                'USER_CREATE', 'USER_READ', 'USER_UPDATE', 'USER_DELETE', 'USER_BAN',
                'ROLE_CREATE', 'ROLE_READ', 'ROLE_UPDATE', 'ROLE_DELETE', 'ROLE_ASSIGN',
                'PROJECT_CREATE', 'PROJECT_READ', 'PROJECT_UPDATE', 'PROJECT_DELETE', 'PROJECT_ASSIGN',
                'CLIENT_CREATE', 'CLIENT_READ', 'CLIENT_UPDATE', 'CLIENT_DELETE',
                'INVOICE_CREATE', 'INVOICE_READ', 'INVOICE_UPDATE', 'INVOICE_DELETE', 'INVOICE_VALIDATE',
                'CONTENT_CREATE', 'CONTENT_READ', 'CONTENT_UPDATE', 'CONTENT_DELETE', 'CONTENT_PUBLISH',
                'REPORT_VIEW', 'REPORT_EXPORT', 'REPORT_ANALYTICS',
                'SYSTEM_CONFIG', 'SYSTEM_BACKUP', 'SYSTEM_LOGS', 'SYSTEM_MONITOR',
                'SUPPORT_CREATE', 'SUPPORT_READ', 'SUPPORT_UPDATE', 'SUPPORT_DELETE', 'SUPPORT_ASSIGN',
                'FORMATION_CREATE', 'FORMATION_READ', 'FORMATION_UPDATE', 'FORMATION_DELETE', 'FORMATION_TEACH'
            ]),
            
            ('ADMINISTRATEUR', 'Administrateur', 8, [
                'USER_CREATE', 'USER_READ', 'USER_UPDATE',
                'ROLE_READ',
                'PROJECT_CREATE', 'PROJECT_READ', 'PROJECT_UPDATE', 'PROJECT_DELETE', 'PROJECT_ASSIGN',
                'CLIENT_CREATE', 'CLIENT_READ', 'CLIENT_UPDATE', 'CLIENT_DELETE',
                'INVOICE_CREATE', 'INVOICE_READ', 'INVOICE_UPDATE', 'INVOICE_DELETE', 'INVOICE_VALIDATE',
                'CONTENT_CREATE', 'CONTENT_READ', 'CONTENT_UPDATE', 'CONTENT_DELETE', 'CONTENT_PUBLISH',
                'REPORT_VIEW', 'REPORT_EXPORT', 'REPORT_ANALYTICS',
                'SUPPORT_CREATE', 'SUPPORT_READ', 'SUPPORT_UPDATE', 'SUPPORT_DELETE', 'SUPPORT_ASSIGN',
                'FORMATION_CREATE', 'FORMATION_READ', 'FORMATION_UPDATE', 'FORMATION_DELETE'
            ]),
            
            ('CHEF_PROJET', 'Chef de Projet', 6, [
                'PROJECT_CREATE', 'PROJECT_READ', 'PROJECT_UPDATE', 'PROJECT_ASSIGN',
                'CLIENT_READ', 'CLIENT_UPDATE',
                'INVOICE_READ', 'INVOICE_UPDATE',
                'CONTENT_READ', 'CONTENT_UPDATE',
                'REPORT_VIEW', 'REPORT_EXPORT',
                'SUPPORT_READ', 'SUPPORT_UPDATE', 'SUPPORT_ASSIGN'
            ]),
            
            ('DEVELOPPEUR', 'Développeur', 5, [
                'PROJECT_READ', 'PROJECT_UPDATE',
                'CONTENT_READ', 'CONTENT_UPDATE',
                'REPORT_VIEW'
            ]),
            
            ('DESIGNER', 'Designer', 5, [
                'PROJECT_READ', 'PROJECT_UPDATE',
                'CONTENT_READ', 'CONTENT_UPDATE',
                'REPORT_VIEW'
            ]),
            
            ('COMMERCIAL', 'Commercial', 5, [
                'CLIENT_CREATE', 'CLIENT_READ', 'CLIENT_UPDATE',
                'PROJECT_READ',
                'INVOICE_CREATE', 'INVOICE_READ',
                'REPORT_VIEW', 'REPORT_EXPORT'
            ]),
            
            ('COMPTABLE', 'Comptable', 6, [
                'CLIENT_READ',
                'INVOICE_CREATE', 'INVOICE_READ', 'INVOICE_UPDATE', 'INVOICE_VALIDATE',
                'REPORT_VIEW', 'REPORT_EXPORT'
            ]),
            
            ('RH', 'Ressources Humaines', 6, [
                'USER_CREATE', 'USER_READ', 'USER_UPDATE',
                'ROLE_READ',
                'REPORT_VIEW', 'REPORT_EXPORT'
            ]),
            
            ('SUPPORT', 'Support Technique', 4, [
                'SUPPORT_CREATE', 'SUPPORT_READ', 'SUPPORT_UPDATE',
                'CLIENT_READ',
                'REPORT_VIEW'
            ]),
            
            ('CLIENT', 'Client', 2, [
                'PROJECT_READ',
                'INVOICE_READ'
            ]),
            
            ('COLLABORATEUR', 'Collaborateur', 4, [
                'PROJECT_READ', 'PROJECT_UPDATE',
                'CONTENT_READ',
                'REPORT_VIEW'
            ]),
            
            ('FORMATEUR', 'Formateur', 5, [
                'FORMATION_CREATE', 'FORMATION_READ', 'FORMATION_UPDATE', 'FORMATION_TEACH',
                'CONTENT_READ', 'CONTENT_UPDATE',
                'REPORT_VIEW'
            ]),
            
            ('STAGIAIRE', 'Stagiaire', 1, [
                'FORMATION_READ',
                'CONTENT_READ'
            ])
        ]
        
        created_roles = []
        for nom, description, niveau, permission_codes in roles_data:
            role, created = Role.objects.get_or_create(
                nom=nom,
                defaults={
                    'description': description,
                    'niveau_hierarchique': niveau,
                    'est_actif': True
                }
            )
            
            if created:
                # Ajouter les permissions au rôle
                permissions = Permission.objects.filter(code__in=permission_codes)
                role.permissions.add(*permissions)
                created_roles.append(role)
                self.stdout.write(f'  ✓ Rôle créé: {description} ({len(permissions)} permissions)')
            else:
                # Mettre à jour les permissions existantes
                permissions = Permission.objects.filter(code__in=permission_codes)
                role.permissions.set(permissions)
                self.stdout.write(f'  ✓ Rôle mis à jour: {description}')
        
        self.stdout.write(f'\n{len(created_roles)} rôles créés/mis à jour avec succès!')
        
        # Création du super admin par défaut
        self.stdout.write('\nCréation du super administrateur par défaut...')
        
        try:
            super_admin = CustomUser.objects.create_superuser(
                username='superadmin',
                email='superadmin@mupenda.com',
                password='Admin123!',
                first_name='Super',
                last_name='Administrateur',
                is_staff=True,
                is_superuser=True,
                est_actif=True
            )
            
            # Attribuer le rôle SUPER_ADMIN
            super_admin_role = Role.objects.get(nom='SUPER_ADMIN')
            UserRole.objects.create(
                utilisateur=super_admin,
                role=super_admin_role,
                est_actif=True
            )
            
            self.stdout.write(self.style.SUCCESS('  ✓ Super administrateur créé avec succès!'))
            self.stdout.write(self.style.WARNING('    Identifiant: superadmin'))
            self.stdout.write(self.style.WARNING('    Mot de passe: Admin123!'))
            self.stdout.write(self.style.WARNING('    Email: superadmin@mupenda.com'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Erreur lors de la création du super admin: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Peuplement initial terminé avec succès!'))
