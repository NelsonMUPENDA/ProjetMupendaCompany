# passenger_wsgi.py
import sys
import os

# Ajoutez le chemin de votre projet au sys.path
# Remplacez '/home/votre_utilisateur/votre_app_root' par le chemin absolu
# que vous allez créer dans cPanel (voir Phase 2, étape 2)
project_home = '/home/mupendac/mupenda.cd'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'MupendaCompany.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()