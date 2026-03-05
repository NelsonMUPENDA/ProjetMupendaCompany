from django.core.management.base import BaseCommand
from MupendaApp.models import Post, CustomUser
from django.utils.text import slugify
from django.utils import timezone


class Command(BaseCommand):
    help = 'Add 10 sample blog posts with different categories'

    def handle(self, *args, **options):
        # Get the first user as author
        author = CustomUser.objects.first()
        if not author:
            self.stdout.write(self.style.ERROR('Aucun utilisateur trouvé. Créez d\'abord un utilisateur.'))
            return

        articles = [
            {
                'titre': 'Les tendances technologiques 2024 qui transformeront votre entreprise',
                'category': 'Technologie',
                'content': '<p>Découvrez les innovations technologiques majeures de 2024 : intelligence artificielle générative, computing quantique, edge computing et bien plus encore. Ces technologies redéfinissent la façon dont les entreprises opèrent et interagissent avec leurs clients.</p><p>L\'adoption rapide de ces outils permet aux entreprises de gagner en efficacité et de créer de nouvelles opportunités de croissance.</p>'
            },
            {
                'titre': 'L\'innovation dans le développement logiciel africain',
                'category': 'Innovation',
                'content': '<p>L\'écosystème tech africain connaît une croissance explosive. Les startups locales développent des solutions innovantes adaptées aux réalités du continent, from fintech to agritech.</p><p>Ces innovations ne résolvent pas seulement des problèmes locaux, mais inspirent également le monde entier avec des approches créatives et durables.</p>'
            },
            {
                'titre': 'Comment le digital transforme les PME congolaises',
                'category': 'Business',
                'content': '<p>La transformation digitale n\'est plus une option pour les PME congolaises. C\'est une nécessité pour rester compétitif dans un marché en évolution rapide. Découvrez les stratégies gagnantes.</p><p>De la digitalisation des processus à l\'adoption du e-commerce, les entreprises qui embrassent le changement sécurisent leur avenir.</p>'
            },
            {
                'titre': 'Cybersécurité : protéger votre entreprise des menaces modernes',
                'category': 'Cybersécurité',
                'content': '<p>Les cyberattaques sont en hausse de 40% en Afrique. Découvrez les meilleures pratiques pour sécuriser vos données et protéger votre entreprise contre les ransomwares, phishing et autres menaces.</p><p>La sensibilisation des employés et les outils de sécurité appropriés sont essentiels pour une défense efficace.</p>'
            },
            {
                'titre': 'Le Cloud : levier de croissance pour les entreprises africaines',
                'category': 'Cloud',
                'content': '<p>Le cloud computing offre aux entreprises africaines une flexibilité et une scalabilité sans précédent. Réduction des coûts infrastructure, accès à des outils enterprise-grade, collaboration à distance : les avantages sont nombreux.</p><p>Les solutions cloud hybrides et multi-cloud gagnent en popularité sur le continent.</p>'
            },
            {
                'titre': 'Intelligence Artificielle : cas d\'usage concrets pour votre business',
                'category': 'IA & Data',
                'content': '<p>L\'IA n\'est plus réservée aux grandes multinationales. Découvrez comment les PME peuvent exploiter l\'intelligence artificielle pour automatiser, personnaliser et prédire.</p><p>De l\'analyse prédictive à l\'automatisation du service client, l\'IA transforme chaque aspect de l\'entreprise moderne.</p>'
            },
            {
                'titre': '5G en Afrique : opportunités et défis du déploiement',
                'category': 'Technologie',
                'content': '<p>La 5G arrive progressivement en Afrique. Quelles sont les opportunités pour les entreprises et les défis techniques et réglementaires à surmonter ?</p><p>Cette nouvelle technologie promet de révolutionner l\'IoT, la télémédecine et les smart cities sur le continent.</p>'
            },
            {
                'titre': 'Fintech : révolution du paiement digital en RDC',
                'category': 'Innovation',
                'content': '<p>Le secteur fintech congolais connaît une effervescence sans précédent. Mobile money, solutions de paiement innovantes, inclusion financière : le paysage évolue rapidement.</p><p>Ces innovations facilitent les transactions quotidiennes et ouvrent de nouvelles perspectives économiques.</p>'
            },
            {
                'titre': 'Stratégie digitale : comment attirer plus de clients en ligne',
                'category': 'Business',
                'content': '<p>Le marketing digital est essentiel pour toute entreprise moderne. SEO, réseaux sociaux, content marketing : découvrez les stratégies qui fonctionnent vraiment en contexte africain.</p><p>Une présence en ligne bien orchestrée peut transformer radicalement la visibilité et les revenus d\'une entreprise.</p>'
            },
            {
                'titre': 'Zero Trust : le nouveau paradigme de sécurité incontournable',
                'category': 'Cybersécurité',
                'content': '<p>Le modèle Zero Trust révolutionne la sécurité informatique. Ne faites confiance à personne, vérifiez tout. Découvrez comment implémenter cette approche dans votre organisation.</p><p>Dans un monde du travail de plus en plus décentralisé, Zero Trust devient une nécessité absolue.</p>'
            }
        ]

        count = 0
        for article in articles:
            slug = slugify(article['titre'])
            # Check if post already exists
            if not Post.objects.filter(slug=slug).exists():
                Post.objects.create(
                    titre=article['titre'],
                    slug=slug,
                    author=author,
                    category=article['category'],
                    content=article['content'],
                    status=1,
                    created_on=timezone.now()
                )
                count += 1
                self.stdout.write(f"✓ Créé : {article['titre'][:50]}... [{article['category']}]")
            else:
                self.stdout.write(f"⚠ Existe déjà : {article['titre'][:50]}...")

        self.stdout.write(self.style.SUCCESS(f'\n✅ {count} articles ajoutés avec succès !'))
