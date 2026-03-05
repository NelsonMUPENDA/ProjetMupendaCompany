from django.core.management.base import BaseCommand
from MupendaApp.models import Formation, Category, CustomUser
from django.utils.text import slugify
from django.utils import timezone


class Command(BaseCommand):
    help = 'Add sample formations to the database'

    def handle(self, *args, **options):
        # Get the first user as formateur
        formateur = CustomUser.objects.first()
        if not formateur:
            self.stdout.write(self.style.ERROR('Aucun utilisateur trouvé. Créez d\'abord un utilisateur.'))
            return

        # Get or create a category
        categorie, _ = Category.objects.get_or_create(name='Développement')

        formations = [
            {
                'nom': 'Développement Web Full-Stack',
                'slug': 'developpement-web-full-stack',
                'description': '<p>Maîtrisez les technologies web modernes : HTML, CSS, JavaScript, Python/Django, et bases de données. Cette formation complète vous permettra de créer des applications web professionnelles de A à Z.</p>',
                'prix': 500,
                'categorie': categorie,
            },
            {
                'nom': 'Cybersécurité & Hacking Éthique',
                'slug': 'cybersecurite-hacking-ethique',
                'description': '<p>Apprenez à sécuriser les systèmes informatiques et à identifier les vulnérabilités. Formation essentielle pour devenir expert en cybersécurité.</p>',
                'prix': 400,
                'categorie': categorie,
            },
            {
                'nom': 'Administration Réseaux',
                'slug': 'administration-reseaux',
                'description': '<p>Configuration, maintenance et sécurisation des réseaux informatiques d\'entreprise. Apprenez à gérer des infrastructures réseau complexes.</p>',
                'prix': 350,
                'categorie': categorie,
            },
            {
                'nom': 'Développement Mobile',
                'slug': 'developpement-mobile',
                'description': '<p>Créez des applications mobiles natives et cross-platform pour iOS et Android. Maîtrisez Flutter et React Native.</p>',
                'prix': 450,
                'categorie': categorie,
            },
            {
                'nom': 'Cloud Computing AWS',
                'slug': 'cloud-computing-aws',
                'description': '<p>Déployez et gérez des infrastructures cloud avec Amazon Web Services. Formation certifiante pour devenir expert cloud.</p>',
                'prix': 500,
                'categorie': categorie,
            },
            {
                'nom': 'Data Science & IA',
                'slug': 'data-science-ia',
                'description': '<p>Analysez les données et créez des modèles d\'intelligence artificielle avec Python. Machine learning et deep learning inclus.</p>',
                'prix': 600,
                'categorie': categorie,
            },
        ]

        count = 0
        for formation_data in formations:
            slug = formation_data.get('slug') or slugify(formation_data['nom'])
            # Check if formation already exists
            if not Formation.objects.filter(slug=slug).exists():
                Formation.objects.create(
                    nom=formation_data['nom'],
                    slug=slug,
                    description=formation_data['description'],
                    prix=formation_data['prix'],
                    categorie=formation_data['categorie'],
                    formateur=formateur,
                    status=1,
                    date_debut=timezone.now().date(),
                    created_on=timezone.now()
                )
                count += 1
                self.stdout.write(f"✓ Créé : {formation_data['nom']}")
            else:
                self.stdout.write(f"⚠ Existe déjà : {formation_data['nom']}")

        self.stdout.write(self.style.SUCCESS(f'\n✅ {count} formations ajoutées avec succès !'))
