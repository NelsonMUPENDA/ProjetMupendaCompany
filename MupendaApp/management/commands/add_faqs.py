from django.core.management.base import BaseCommand
from MupendaApp.models import FAQ, Category
from django.utils import timezone


class Command(BaseCommand):
    help = 'Add sample FAQs to the database'

    def handle(self, *args, **options):
        # Get or create a category for FAQs
        categorie, _ = Category.objects.get_or_create(name='Général')

        faqs = [
            {
                'question': 'Quels types de services proposez-vous ?',
                'reponse': '<p>Nous proposons une gamme complète de services informatiques incluant : réseaux informatiques, cybersécurité, développement d\'applications web et mobiles, conception de logiciels sur mesure, systèmes embarqués, et communication digitale.</p>',
                'ordre_affichage': 1,
            },
            {
                'question': 'Comment puis-je demander un devis ?',
                'reponse': '<p>Vous pouvez demander un devis en nous contactant via le formulaire de contact sur notre site, par email à contact@mupenda.cd, ou en nous appelant directement. Notre équipe vous répondra dans les <strong>24 heures ouvrables</strong>.</p>',
                'ordre_affichage': 2,
            },
            {
                'question': 'Quelle est la durée moyenne d\'un projet ?',
                'reponse': '<p>La durée d\'un projet varie selon sa complexité :</p><ul><li>Un projet simple peut prendre <strong>2-4 semaines</strong></li><li>Un projet moyen nécessite <strong>1-2 mois</strong></li><li>Un projet complexe peut prendre <strong>2-6 mois</strong></li></ul><p>Nous établissons un planning détaillé lors de la phase de conception.</p>',
                'ordre_affichage': 3,
            },
            {
                'question': 'Proposez-vous un support après livraison ?',
                'reponse': '<p>Oui, nous offrons un <strong>support technique après livraison</strong>. Nous proposons différentes formules de maintenance et d\'assistance technique pour garantir le bon fonctionnement de vos solutions dans le temps.</p>',
                'ordre_affichage': 4,
            },
            {
                'question': 'Comment se déroule le processus de développement ?',
                'reponse': '<p>Notre processus comprend <strong>5 étapes</strong> :</p><ol><li>Analyse des besoins</li><li>Conception et proposition</li><li>Développement</li><li>Tests et validation</li><li>Livraison et formation</li></ol><p>Nous maintenons une communication régulière avec vous tout au long du projet.</p>',
                'ordre_affichage': 5,
            },
            {
                'question': 'Proposez-vous des formations ?',
                'reponse': '<p>Oui, nous proposons des <strong>formations personnalisées</strong> sur les technologies que nous utilisons. Nos formations couvrent le développement web, la cybersécurité, les réseaux informatiques, et bien plus encore. Consultez notre page Formations pour plus d\'informations.</p>',
                'ordre_affichage': 6,
            },
            {
                'question': 'Quels sont vos modes de paiement ?',
                'reponse': '<p>Nous acceptons plusieurs modes de paiement :</p><ul><li>Virement bancaire</li><li>Paiement mobile (Mobile Money)</li><li>Paiement en plusieurs tranches selon les étapes du projet</li></ul>',
                'ordre_affichage': 7,
            },
            {
                'question': 'Travaillez-vous avec des clients internationaux ?',
                'reponse': '<p>Oui, nous travaillons avec des clients partout en Afrique et au-delà. Nous avons une expérience éprouvée dans la gestion de projets à distance grâce à nos outils de collaboration modernes.</p>',
                'ordre_affichage': 8,
            },
        ]

        count = 0
        for faq_data in faqs:
            # Check if FAQ already exists
            if not FAQ.objects.filter(question=faq_data['question']).exists():
                FAQ.objects.create(
                    question=faq_data['question'],
                    reponse=faq_data['reponse'],
                    categorie=categorie,
                    ordre_affichage=faq_data['ordre_affichage'],
                    est_active=True,
                    created_on=timezone.now()
                )
                count += 1
                self.stdout.write(f"✓ Créé : {faq_data['question'][:50]}...")
            else:
                self.stdout.write(f"⚠ Existe déjà : {faq_data['question'][:50]}...")

        self.stdout.write(self.style.SUCCESS(f'\n✅ {count} FAQs ajoutées avec succès !'))
