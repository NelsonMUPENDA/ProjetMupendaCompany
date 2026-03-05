#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MupendaCompany.settings')
django.setup()

from MupendaApp.models import CustomUser, Role, Permission, UserRole, Departement, Projet, Tache, Notification, LogAction
from django.utils import timezone

def create_initial_data():
    """Créer les données initiales pour le système"""
    print("🚀 Création des données initiales...")
    
    # 1. Créer les permissions de base
    print("\n📋 Création des permissions...")
    permissions_data = [
        ('UTILISATEUR_AJOUTER', 'Ajouter utilisateur', 'Gestion des utilisateurs', 'UTILISATEUR'),
        ('UTILISATEUR_MODIFIER', 'Modifier utilisateur', 'Modifier les utilisateurs', 'UTILISATEUR'),
        ('UTILISATEUR_SUPPRIMER', 'Supprimer utilisateur', 'Supprimer les utilisateurs', 'UTILISATEUR'),
        ('DEPARTEMENT_AJOUTER', 'Ajouter département', 'Gestion des départements', 'DEPARTEMENT'),
        ('DEPARTEMENT_MODIFIER', 'Modifier département', 'Modifier les départements', 'DEPARTEMENT'),
        ('DEPARTEMENT_SUPPRIMER', 'Supprimer département', 'Supprimer les départements', 'DEPARTEMENT'),
        ('PROJET_AJOUTER', 'Ajouter projet', 'Gestion des projets', 'PROJET'),
        ('PROJET_MODIFIER', 'Modifier projet', 'Modifier les projets', 'PROJET'),
        ('PROJET_SUPPRIMER', 'Supprimer projet', 'Supprimer les projets', 'PROJET'),
        ('TACHE_AJOUTER', 'Ajouter tâche', 'Gestion des tâches', 'TACHE'),
        ('TACHE_MODIFIER', 'Modifier tâche', 'Modifier les tâches', 'TACHE'),
        ('TACHE_SUPPRIMER', 'Supprimer tâche', 'Supprimer les tâches', 'TACHE'),
        ('RAPPORT_VOIR', 'Voir rapports', 'Voir les rapports', 'RAPPORT'),
        ('SYSTEME_ADMIN', 'Administration système', 'Administration système', 'SYSTEME'),
    ]
    
    for code, nom, description, categorie in permissions_data:
        permission, created = Permission.objects.get_or_create(
            code=code,
            defaults={
                'nom': nom,
                'description': description,
                'categorie': categorie
            }
        )
        if created:
            print(f"  ✅ Permission créée: {code}")
    
    # 2. Créer les rôles
    print("\n🛡️ Création des rôles...")
    roles_data = [
        ('SUPER_ADMIN', 'Super Administrateur', [
            'UTILISATEUR_AJOUTER', 'UTILISATEUR_MODIFIER', 'UTILISATEUR_SUPPRIMER',
            'DEPARTEMENT_AJOUTER', 'DEPARTEMENT_MODIFIER', 'DEPARTEMENT_SUPPRIMER',
            'PROJET_AJOUTER', 'PROJET_MODIFIER', 'PROJET_SUPPRIMER',
            'TACHE_AJOUTER', 'TACHE_MODIFIER', 'TACHE_SUPPRIMER',
            'RAPPORT_VOIR', 'SYSTEME_ADMIN'
        ]),
        ('ADMINISTRATEUR', 'Administrateur', [
            'UTILISATEUR_AJOUTER', 'UTILISATEUR_MODIFIER',
            'DEPARTEMENT_AJOUTER', 'DEPARTEMENT_MODIFIER',
            'PROJET_AJOUTER', 'PROJET_MODIFIER',
            'TACHE_AJOUTER', 'TACHE_MODIFIER',
            'RAPPORT_VOIR'
        ]),
        ('CHEF_PROJET', 'Chef de Projet', [
            'PROJET_AJOUTER', 'PROJET_MODIFIER',
            'TACHE_AJOUTER', 'TACHE_MODIFIER',
            'RAPPORT_VOIR'
        ]),
        ('DEVELOPPEUR', 'Développeur', [
            'TACHE_AJOUTER', 'TACHE_MODIFIER',
            'RAPPORT_VOIR'
        ]),
        ('COLLABORATEUR', 'Collaborateur', [
            'RAPPORT_VOIR'
        ]),
        ('CLIENT', 'Client', [
            'RAPPORT_VOIR'
        ]),
        ('FORMATEUR', 'Formateur', [
            'RAPPORT_VOIR'
        ]),
        ('STAGIAIRE', 'Stagiaire', [
            'RAPPORT_VOIR'
        ]),
    ]
    
    for nom, description, permission_codes in roles_data:
        role, created = Role.objects.get_or_create(
            nom=nom,
            defaults={'description': description}
        )
        if created:
            print(f"  ✅ Rôle créé: {nom}")
            # Ajouter les permissions au rôle
            for perm_code in permission_codes:
                try:
                    permission = Permission.objects.get(code=perm_code)
                    role.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"  ⚠️ Permission non trouvée: {perm_code}")
    
    # 3. Créer le super admin
    print("\n👤 Création du Super Admin...")
    super_admin, created = CustomUser.objects.get_or_create(
        username='superadmin',
        defaults={
            'email': 'superadmin@mupenda.com',
            'first_name': 'Super',
            'last_name': 'Admin',
            'telephone': '+243000000000',
            'date_embauche': timezone.now().date(),
            'est_actif': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        super_admin.set_password('admin123')
        super_admin.save()
        print(f"  ✅ Super Admin créé: {super_admin.username}")
        
        # Assigner le rôle SUPER_ADMIN
        role = Role.objects.get(nom='SUPER_ADMIN')
        UserRole.objects.get_or_create(
            utilisateur=super_admin,
            role=role,
            defaults={'date_attribution': timezone.now()}
        )
        print(f"  ✅ Rôle SUPER_ADMIN assigné à {super_admin.username}")
    else:
        print(f"  ℹ️ Super Admin existe déjà: {super_admin.username}")
    
    # 4. Créer des départements
    print("\n🏢 Création des départements...")
    departements_data = [
        ('IT', 'Département Informatique', 'Gestion des systèmes et technologies'),
        ('RH', 'Ressources Humaines', 'Gestion du personnel et recrutement'),
        ('FINANCE', 'Finance', 'Gestion financière et comptabilité'),
        ('MARKETING', 'Marketing', 'Marketing et communication'),
        ('PRODUCTION', 'Production', 'Production et opérations'),
    ]
    
    for nom, description, details in departements_data:
        dept, created = Departement.objects.get_or_create(
            nom=nom,
            defaults={
                'description': description,
                'responsable': super_admin,
                'est_actif': True
            }
        )
        if created:
            print(f"  ✅ Département créé: {nom}")
    
    # 5. Créer des utilisateurs de test
    print("\n👥 Création des utilisateurs de test...")
    users_data = [
        ('admin', 'Administrateur', 'ADMINISTRATEUR', 'admin@mupenda.com'),
        ('chefprojet', 'Chef de Projet', 'CHEF_PROJET', 'chefprojet@mupenda.com'),
        ('dev1', 'Développeur 1', 'DEVELOPPEUR', 'dev1@mupenda.com'),
        ('dev2', 'Développeur 2', 'DEVELOPPEUR', 'dev2@mupenda.com'),
        ('employe1', 'Employé 1', 'COLLABORATEUR', 'employe1@mupenda.com'),
    ]
    
    for username, full_name, role_name, email in users_data:
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': full_name.split()[0],
                'last_name': full_name.split()[-1] if len(full_name.split()) > 1 else '',
                'telephone': f'+243{username}000000',
                'date_embauche': timezone.now().date(),
                'est_actif': True,
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✅ Utilisateur créé: {username}")
            
            # Assigner le rôle
            role = Role.objects.get(nom=role_name)
            UserRole.objects.get_or_create(
                utilisateur=user,
                role=role,
                defaults={'date_attribution': timezone.now()}
            )
            print(f"  ✅ Rôle {role_name} assigné à {username}")
    
    # 6. Créer des projets de test
    print("\n📋 Création des projets de test...")
    projets_data = [
        ('Site Web Mupenda', 'Développement du site web de l\'entreprise', 'IT', 'chefprojet'),
        ('Application Mobile', 'Application mobile pour clients', 'IT', 'chefprojet'),
        ('Système de Paie', 'Système de gestion de paie', 'IT', 'admin'),
        ('Campagne Marketing', 'Campagne marketing Q1 2026', 'MARKETING', 'admin'),
    ]
    
    for nom, description, dept_nom, chef_username in projets_data:
        try:
            dept = Departement.objects.get(nom=dept_nom)
            chef = CustomUser.objects.get(username=chef_username)
            
            projet, created = Projet.objects.get_or_create(
                nom=nom,
                defaults={
                    'description': description,
                    'departement': dept,
                    'chef_projet': chef,
                    'statut': 'EN_COURS',
                    'priorite': 'MOYENNE',
                    'date_debut': timezone.now().date(),
                    'date_fin_prevue': timezone.now().date() + timezone.timedelta(days=90),
                    'budget': 10000.00,
                    'progression': 25,
                    'est_actif': True,
                    'cree_par': super_admin
                }
            )
            if created:
                print(f"  ✅ Projet créé: {nom}")
                
                # Ajouter l'équipe
                equipe = CustomUser.objects.filter(
                    user_roles__role__nom__in=['DEVELOPPEUR', 'ADMINISTRATEUR']
                )[:3]
                projet.equipe.add(*equipe)
        except (Departement.DoesNotExist, CustomUser.DoesNotExist) as e:
            print(f"  ⚠️ Erreur création projet {nom}: {e}")
    
    # 7. Créer des tâches de test
    print("\n📝 Création des tâches de test...")
    taches_data = [
        ('Design UI/UX', 'Création des maquettes', 'MOYENNE', 'Site Web Mupenda', 'dev1'),
        ('Backend API', 'Développement des APIs', 'HAUTE', 'Site Web Mupenda', 'dev2'),
        ('Base de données', 'Configuration de la BDD', 'HAUTE', 'Site Web Mupenda', 'dev1'),
        ('Tests', 'Tests unitaires et intégration', 'MOYENNE', 'Application Mobile', 'dev2'),
    ]
    
    for titre, description, priorite, projet_nom, assigne_username in taches_data:
        try:
            projet = Projet.objects.get(nom=projet_nom)
            assigne = CustomUser.objects.get(username=assigne_username)
            
            tache, created = Tache.objects.get_or_create(
                titre=titre,
                defaults={
                    'description': description,
                    'projet': projet,
                    'assigne_a': assigne,
                    'priorite': priorite,
                    'statut': 'EN_COURS',
                    'date_echeance': timezone.now().date() + timezone.timedelta(days=30),
                    'cree_par': super_admin
                }
            )
            if created:
                print(f"  ✅ Tâche créée: {titre}")
        except (Projet.DoesNotExist, CustomUser.DoesNotExist) as e:
            print(f"  ⚠️ Erreur création tâche {titre}: {e}")
    
    # 8. Créer des notifications de test
    print("\n🔔 Création des notifications de test...")
    notifications_data = [
        ('superadmin', 'Bienvenue!', 'Bienvenue dans le système de gestion Mupenda Company', 'INFO'),
        ('admin', 'Nouveaux projets', 'Deux nouveaux projets ont été créés', 'INFO'),
        ('chefprojet', 'Tâches assignées', 'Vous avez 3 nouvelles tâches assignées', 'INFO'),
        ('dev1', 'Nouvelle tâche', 'Une nouvelle tâche vous a été assignée', 'INFO'),
    ]
    
    for username, titre, message, type_notif in notifications_data:
        try:
            utilisateur = CustomUser.objects.get(username=username)
            notification, created = Notification.objects.get_or_create(
                titre=titre,
                destinataire=utilisateur,
                defaults={
                    'message': message,
                    'type_notification': type_notif,
                    'est_lue': False
                }
            )
            if created:
                print(f"  ✅ Notification créée pour {username}: {titre}")
        except CustomUser.DoesNotExist:
            print(f"  ⚠️ Utilisateur non trouvé: {username}")
    
    print("\n🎉 Données initiales créées avec succès!")
    print("\n🔑 Identifiants de connexion:")
    print("  Super Admin: superadmin / admin123")
    print("  Admin: admin / password123")
    print("  Chef Projet: chefprojet / password123")
    print("  Développeur 1: dev1 / password123")
    print("  Développeur 2: dev2 / password123")
    print("  Employé 1: employe1 / password123")

if __name__ == '__main__':
    create_initial_data()
