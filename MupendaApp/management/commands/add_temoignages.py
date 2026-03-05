from django.core.management.base import BaseCommand
from MupendaApp.models import TemoignageClient, CustomUser
from django.utils import timezone


class Command(BaseCommand):
    help = 'Add sample testimonials to the database'

    def handle(self, *args, **options):
        # Get the first user as author
        author = CustomUser.objects.first()
        if not author:
            self.stdout.write(self.style.ERROR('Aucun utilisateur trouvé. Créez d\'abord un utilisateur.'))
            return

        temoignages = [
            {
                'nom': 'Kasongo',
                'prenom': 'Jean-Marc',
                'message': '<p>Équipe professionnelle et réactive. Notre projet a été livré dans les délais avec une qualité exceptionnelle. Mupenda a su comprendre nos besoins et proposer des solutions adaptées à notre entreprise.</p>',
            },
            {
                'nom': 'Mukendi',
                'prenom': 'Sarah',
                'message': '<p>Une transformation digitale réussie grâce à l\'expertise de Mupenda. Leur accompagnement sur mesure a fait toute la différence dans la modernisation de nos processus.</p>',
            },
            {
                'nom': 'Lumbala',
                'prenom': 'Paul',
                'message': '<p>Excellent rapport qualité-prix. L\'équipe a su comprendre nos besoins et proposer des solutions innovantes. Je recommande vivement leurs services pour tout projet digital.</p>',
            },
            {
                'nom': 'Ilunga',
                'prenom': 'Marie-Claire',
                'message': '<p>Service client impeccable et livraisons toujours dans les temps. Mupenda est devenu notre partenaire technologique de confiance pour tous nos projets digitaux.</p>',
            },
            {
                'nom': 'Tshibangu',
                'prenom': 'Patrick',
                'message': '<p>La formation dispensée par Mupenda a été transformative pour notre équipe. Nous avons gagné en productivité et en compétences techniques. Merci pour ce service de qualité !</p>',
            },
            {
                'nom': 'Kapinga',
                'prenom': 'Dorothy',
                'message': '<p>Application mobile développée avec soin et professionnalisme. Notre clientèle adore la nouvelle expérience utilisateur. Bravo à toute l\'équipe de Mupenda !</p>',
            },
        ]

        count = 0
        for temoignage_data in temoignages:
            # Check if testimonial already exists (by nom + prenom)
            if not TemoignageClient.objects.filter(
                nom=temoignage_data['nom'],
                prenom=temoignage_data['prenom']
            ).exists():
                TemoignageClient.objects.create(
                    nom=temoignage_data['nom'],
                    prenom=temoignage_data['prenom'],
                    message=temoignage_data['message'],
                    auteur=author,
                    status=1,  # Published
                    created_on=timezone.now()
                )
                count += 1
                self.stdout.write(f"✓ Créé : {temoignage_data['prenom']} {temoignage_data['nom']}")
            else:
                self.stdout.write(f"⚠ Existe déjà : {temoignage_data['prenom']} {temoignage_data['nom']}")

        self.stdout.write(self.style.SUCCESS(f'\n✅ {count} témoignages ajoutés avec succès !'))
