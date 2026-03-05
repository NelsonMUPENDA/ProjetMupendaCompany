from django.core.management.base import BaseCommand
from MupendaApp.models import Partenaire
from django.utils import timezone


class Command(BaseCommand):
    help = 'Add sample partners to the database'

    def handle(self, *args, **options):
        partenaires = [
            {
                'nom': 'TechCorp Africa',
                'site_web': 'https://techcorp.africa',
                'description': 'Leader des solutions technologiques en Afrique',
                'email_contact': 'contact@techcorp.africa',
                'telephone': '+243 123 456 789',
                'ordre_affichage': 1,
            },
            {
                'nom': 'Innovation RDC',
                'site_web': 'https://innovation-rdc.cd',
                'description': 'Partenaire innovation et transformation digitale',
                'email_contact': 'info@innovation-rdc.cd',
                'telephone': '+243 987 654 321',
                'ordre_affichage': 2,
            },
            {
                'nom': 'Cloud Solutions',
                'site_web': 'https://cloudsolutions.com',
                'description': 'Expert en infrastructure cloud et hébergement',
                'email_contact': 'support@cloudsolutions.com',
                'telephone': '+243 456 789 012',
                'ordre_affichage': 3,
            },
            {
                'nom': 'Digital Africa',
                'site_web': 'https://digital-africa.org',
                'description': 'Organisation promotion du digital en Afrique',
                'email_contact': 'partenariat@digital-africa.org',
                'telephone': '+243 789 012 345',
                'ordre_affichage': 4,
            },
        ]

        count = 0
        for partenaire_data in partenaires:
            # Check if partner already exists
            if not Partenaire.objects.filter(nom=partenaire_data['nom']).exists():
                Partenaire.objects.create(
                    **partenaire_data,
                    est_actif=True,
                    created_on=timezone.now()
                )
                count += 1
                self.stdout.write(f"✓ Créé : {partenaire_data['nom']}")
            else:
                self.stdout.write(f"⚠ Existe déjà : {partenaire_data['nom']}")

        self.stdout.write(self.style.SUCCESS(f'\n✅ {count} partenaires ajoutés avec succès !'))
