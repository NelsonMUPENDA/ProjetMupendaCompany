# Mupenda Company - Application Web Django

## 📋 Vue d'ensemble

Mupenda Company est une application web complète développée avec Django, conçue pour présenter les services, formations, réalisations et informations d'une entreprise technologique basée en RDC et opérant en Afrique.

## 🚀 Fonctionnalités principales

### 1. **Site Web Public**
- **Page d'accueil** : Présentation de l'entreprise avec statistiques, services, témoignages et partenaires
- **Services** : Liste et détail des services proposés
- **Formations** : Catalogue de formations avec possibilité d'inscription
- **Réalisations/Portfolio** : Showcase des projets réalisés
- **Blog** : Articles et actualités de l'entreprise
- **À propos** : Informations sur l'entreprise, mission, valeurs et objectifs
- **FAQ** : Questions fréquentes
- **Contact** : Formulaire de contact et informations de l'entreprise
- **Pages légales** : CGU, Politique de confidentialité, Mentions légales

### 2. **Espace Membre**
- Inscription et connexion des utilisateurs
- Profil utilisateur personnalisable
- Tableau de bord personnel
- Gestion des demandes de devis
- Notifications

### 3. **Système de Gestion d'Entreprise (Admin)**
- **Gestion des utilisateurs** avec rôles et permissions avancées
- **Gestion des clients** et historique d'interactions
- **Gestion des projets** et suivi des tâches
- **Gestion des collaborateurs** et affectations aux projets
- **Suivi du temps** et calcul des coûts
- **Gestion des formations**
- **Gestion des demandes de devis**
- **Newsletter** : Gestion des abonnés et envoi de campagnes

## 🛠️ Stack Technique

- **Backend** : Django 5.x
- **Base de données** : SQLite (développement) / PostgreSQL (production recommandée)
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap
- **Éditeur de texte riche** : CKEditor 5
- **Authentification** : Django Auth avec système de rôles personnalisé

## 📁 Structure du projet

```
MupendaCompany/
├── MupendaCompany/          # Configuration principale Django
│   ├── settings.py          # Paramètres de l'application
│   ├── urls.py             # Routes principales
│   └── wsgi.py             # Configuration WSGI
│
├── MupendaApp/             # Application principale
│   ├── models.py           # Modèles de données
│   ├── views.py            # Logiques métier et vues
│   ├── forms.py            # Formulaires
│   ├── admin.py            # Configuration de l'admin
│   ├── urls.py             # Routes de l'application
│   ├── templates/          # Templates HTML
│   │   ├── base.html       # Template de base
│   │   ├── index.html      # Page d'accueil
│   │   ├── formation*.html # Pages formations
│   │   ├── service*.html   # Pages services
│   │   ├── blog*.html      # Pages blog
│   │   ├── dashboard/      # Templates d'administration
│   │   └── ...
│   ├── static/             # Fichiers statiques (CSS, JS, images)
│   └── management/         # Commandes personnalisées
│
├── media/                  # Fichiers uploadés par les utilisateurs
├── staticfiles/           # Fichiers statiques collectés (production)
├── manage.py              # Script de gestion Django
└── requirements.txt       # Dépendances Python
```

## 🗃️ Modèles de données principaux

### Modèles de contenu
| Modèle | Description |
|--------|-------------|
| `Services` | Services proposés par l'entreprise |
| `Formation` | Formations disponibles avec dates, prix, formateur |
| `Realisation` | Projets réalisés (portfolio) |
| `Post` | Articles de blog |
| `Category` | Catégories pour formations, blog et réalisations |
| `TemoignageClient` | Témoignages des clients |
| `Partenaire` | Partenaires de l'entreprise |
| `FAQ` | Questions fréquentes |
| `PageLegale` | Pages légales (CGU, Politique, Mentions) |
| `Apropos` | Contenu de la page "À propos" |
| `SiteContact` | Informations de contact du site |

### Modèles de gestion d'entreprise
| Modèle | Description |
|--------|-------------|
| `CustomUser` | Utilisateurs avec rôles personnalisés |
| `Role` / `Permission` / `UserRole` | Système de gestion des accès |
| `Client` | Gestion des clients |
| `HistoriqueInteraction` | Suivi des interactions avec les clients |
| `AssociationClientProjet` | Liaison clients-projets |
| `Projet` | Gestion des projets internes |
| `Departement` | Départements de l'entreprise |
| `Tache` | Tâches associées aux projets |
| `AffectationCollaborateur` | Affectation des collaborateurs aux projets |
| `SuiviTemps` | Suivi du temps passé sur les projets |
| `Devis` | Demandes de devis des clients |
| `NewsletterSubscriber` / `NewsletterCampaign` | Gestion newsletter |

## ⚙️ Installation et configuration

### Prérequis
- Python 3.10+
- pip
- virtualenv (recommandé)

### Installation

1. **Cloner le projet**
```bash
git clone <url_du_projet>
cd MupendaCompany
```

2. **Créer un environnement virtuel**
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Collecter les fichiers statiques** (production)
```bash
python manage.py collectstatic
```

7. **Lancer le serveur de développement**
```bash
python manage.py runserver
# ou pour un réseau local
python manage.py runserver 0.0.0.0:8000
```

L'application est accessible à l'adresse : http://127.0.0.1:8000/

## 👤 Rôles utilisateurs

Le système dispose d'un système de rôles avancé :

- **SUPER_ADMIN** : Accès total à toutes les fonctionnalités
- **ADMINISTRATEUR** : Gestion du site et contenu
- **GERANT** : Gestion des projets et collaborateurs
- **CHEF_PROJET** : Gestion de projets spécifiques
- **COMMERCIAL** : Gestion des clients et devis
- **COMPTABLE** : Gestion financière
- **TECHNICIEN** : Accès aux tâches techniques
- **CLIENT** : Espace client
- **UTILISATEUR** : Utilisateur standard

## 🔐 Accès admin

- URL : `/admin/`
- Identifiants : créés via `createsuperuser`

## 📧 Fonctionnalités de newsletter

- Inscription des visiteurs à la newsletter
- Gestion des abonnés dans l'admin
- Création et envoi de campagnes
- Statistiques d'ouverture

## 💰 Système de devis

- Formulaire de demande de devis pour les visiteurs
- Gestion des demandes dans l'admin
- Workflow de validation/refus
- Réponse personnalisée avec montant proposé

## 🔧 Commandes personnalisées

Le dossier `management/commands/` contient des commandes utilitaires :
- `add_formations.py` : Peuplement de formations de test
- Autres commandes de maintenance

Pour exécuter une commande :
```bash
python manage.py add_formations
```

## 📝 Notes importantes

### Images par défaut
L'application utilise des images par défaut pour :
- `default-formation.jpg` : Image par défaut des formations
- `default-avatar.png` : Avatar par défaut des utilisateurs

Ces fichiers doivent être placés dans `MupendaApp/static/images/`

### Configuration email
Pour l'envoi d'emails (newsletter, notifications), configurer dans `settings.py` :
```python
EMAIL_HOST = 'votre_smtp'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'votre_email'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'
```

### Sécurité
- Ne jamais committer le fichier `settings.py` avec des secrets en production
- Utiliser des variables d'environnement pour les données sensibles
- Activer HTTPS en production

## 🌐 URLs principales

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil |
| `/admin/` | Interface d'administration |
| `/formation/` | Liste des formations |
| `/formation/<slug>/` | Détail d'une formation |
| `/service/` | Liste des services |
| `/service/<slug>/` | Détail d'un service |
| `/blog/` | Blog |
| `/blog/<slug>/` | Article de blog |
| `/realisations/` | Portfolio |
| `/apropos/` | À propos |
| `/contact/` | Contact |
| `/faq/` | FAQ |
| `/connexion/` | Connexion |
| `/inscription/` | Inscription |
| `/profil/` | Profil utilisateur |

## 🤝 Support et contact

Pour toute question ou suggestion concernant l'application, veuillez contacter l'équipe de développement.

---

**Mupenda Company** - Votre partenaire technologique de confiance en RDC et en Afrique 🌍
