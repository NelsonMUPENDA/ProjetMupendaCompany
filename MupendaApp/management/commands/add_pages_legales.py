from django.core.management.base import BaseCommand
from MupendaApp.models import PageLegale
from django.utils import timezone


class Command(BaseCommand):
    help = 'Add legal pages content to the database (CGU and Politique)'

    def handle(self, *args, **options):
        # CGU Content
        cgu_content = """<div class="cgu-article">
  <h2><i class="bi bi-1-circle-fill"></i> Objet des Conditions</h2>
  <p>Les présentes Conditions Générales d'Utilisation (CGU) ont pour objet de définir les modalités et conditions dans lesquelles <strong>Mupenda Company</strong> met à disposition des utilisateurs ses services et produits, ainsi que les modalités et conditions dans lesquelles les utilisateurs accèdent et utilisent ces services.</p>
  <p>Toute utilisation des services de Mupenda implique l'acceptation sans réserve des présentes CGU.</p>
</div>

<div class="cgu-article">
  <h2><i class="bi bi-2-circle-fill"></i> Services Proposés</h2>
  <p>Mupenda Company propose les services suivants :</p>
  <ul>
    <li>Réseaux informatiques et télécommunications</li>
    <li>Cybersécurité et protection des données</li>
    <li>Développement d'applications web et mobiles</li>
    <li>Conception de logiciels sur mesure</li>
    <li>Systèmes embarqués et IoT</li>
    <li>Communication digitale et marketing</li>
    <li>Formations professionnelles</li>
  </ul>
</div>

<div class="cgu-article">
  <h2><i class="bi bi-3-circle-fill"></i> Accès aux Services</h2>
  <p>L'accès aux services est réservé aux utilisateurs disposant d'une connexion Internet et des équipements nécessaires. Mupenda s'efforce de maintenir les services accessibles 7j/7 et 24h/24, mais ne peut garantir une disponibilité permanente en raison des contraintes techniques et de maintenance.</p>
  <p>Des interruptions temporaires peuvent être nécessaires pour des raisons de maintenance, de mise à jour ou de force majeure. Mupenda informera les utilisateurs des interruptions programmées dans la mesure du possible.</p>
</div>

<div class="cgu-article">
  <h2><i class="bi bi-4-circle-fill"></i> Obligations des Utilisateurs</h2>
  <p>L'utilisateur s'engage à :</p>
  <ul>
    <li>Fournir des informations exactes, complètes et à jour lors de l'utilisation des services</li>
    <li>Ne pas utiliser les services à des fins illégales ou non autorisées</li>
    <li>Ne pas tenter de porter atteinte à la sécurité des systèmes de Mupenda</li>
    <li>Respecter les droits de propriété intellectuelle de Mupenda et des tiers</li>
    <li>Ne pas diffuser de contenu diffamatoire, injurieux ou portant atteinte aux droits d'autrui</li>
  </ul>
</div>

<div class="cgu-article">
  <h2><i class="bi bi-5-circle-fill"></i> Propriété Intellectuelle</h2>
  <p>L'ensemble des éléments constituant le site et les services de Mupenda (textes, graphismes, logos, images, vidéos, sons, logiciels, marques, etc.) sont la propriété exclusive de Mupenda ou de ses partenaires et sont protégés par les lois relatives à la propriété intellectuelle.</p>
  <p>Toute reproduction, représentation, modification, publication, transmission, ou plus généralement toute exploitation non autorisée des éléments du site et des services est strictement interdite sans l'accord préalable écrit de Mupenda.</p>
</div>

<div class="cgu-article">
  <h2><i class="bi bi-6-circle-fill"></i> Responsabilités</h2>
  <p>Mupenda s'engage à mettre en œuvre tous les moyens nécessaires pour assurer la qualité de ses services, mais ne peut garantir l'exhaustivité, l'exactitude ou l'absence d'erreurs dans les informations fournies.</p>
  <p>Mupenda ne saurait être tenu responsable des dommages résultant de l'utilisation des services, notamment en cas de force majeure, de dysfonctionnement du réseau Internet, ou de toute autre cause échappant à son contrôle raisonnable.</p>
</div>

<div class="cgu-article">
  <h2><i class="bi bi-7-circle-fill"></i> Modification des CGU</h2>
  <p>Mupenda se réserve le droit de modifier les présentes CGU à tout moment. Les modifications entrent en vigueur dès leur publication sur le site. Il est de la responsabilité de l'utilisateur de consulter régulièrement les CGU pour prendre connaissance des éventuelles modifications.</p>
  <p>L'utilisation continue des services après publication des modifications constitue une acceptation des nouvelles CGU.</p>
</div>

<div class="cgu-article">
  <h2><i class="bi bi-8-circle-fill"></i> Droit Applicable et Juridiction</h2>
  <p>Les présentes CGU sont régies par les lois de la République Démocratique du Congo. Tout litige relatif à l'interprétation ou à l'exécution des présentes CGU sera soumis aux tribunaux compétents de Goma, à défaut d'accord amiable entre les parties.</p>
</div>"""

        # Politique Content
        politique_content = """<div class="privacy-article">
  <h2><i class="bi bi-1-circle-fill"></i> Introduction</h2>
  <p>La présente Politique de Confidentialité décrit comment <strong>Mupenda Company</strong> collecte, utilise, conserve et protège vos données personnelles lorsque vous utilisez nos services et visitez notre site web.</p>
  <p>En utilisant nos services, vous acceptez les pratiques décrites dans cette politique. Nous nous engageons à protéger votre vie privée et à traiter vos données avec la plus grande confidentialité.</p>
</div>

<div class="privacy-article">
  <h2><i class="bi bi-2-circle-fill"></i> Données Collectées</h2>
  <p>Nous pouvons collecter les types de données suivants :</p>
  <ul>
    <li><strong>Informations d'identification</strong> : nom, prénom, adresse email, numéro de téléphone</li>
    <li><strong>Informations professionnelles</strong> : entreprise, poste, secteur d'activité</li>
    <li><strong>Données de connexion</strong> : adresse IP, type de navigateur, pages visitées</li>
    <li><strong>Informations de projet</strong> : description de vos besoins et objectifs</li>
  </ul>
</div>

<div class="privacy-article">
  <h2><i class="bi bi-3-circle-fill"></i> Utilisation des Données</h2>
  <p>Vos données personnelles sont utilisées pour :</p>
  <ul>
    <li>Fournir et améliorer nos services</li>
    <li>Communiquer avec vous concernant vos demandes et projets</li>
    <li>Vous envoyer des informations sur nos services (avec votre consentement)</li>
    <li>Respecter nos obligations légales et réglementaires</li>
    <li>Prévenir la fraude et assurer la sécurité de nos systèmes</li>
  </ul>
</div>

<div class="privacy-article">
  <h2><i class="bi bi-4-circle-fill"></i> Protection des Données</h2>
  <p>Nous mettons en œuvre des mesures de sécurité techniques et organisationnelles appropriées pour protéger vos données personnelles contre tout accès non autorisé, modification, divulgation ou destruction.</p>
  <p>Ces mesures incluent :</p>
  <ul>
    <li>Chiffrement des données sensibles</li>
    <li>Contrôles d'accès stricts</li>
    <li>Surveillance régulière de nos systèmes</li>
    <li>Formation de notre personnel aux bonnes pratiques de sécurité</li>
  </ul>
</div>

<div class="privacy-article">
  <h2><i class="bi bi-5-circle-fill"></i> Partage des Données</h2>
  <p>Nous ne vendons, n'échangeons ni ne transférons vos données personnelles à des tiers sans votre consentement, sauf dans les cas suivants :</p>
  <ul>
    <li>Lorsque cela est nécessaire pour fournir nos services (sous-traitants)</li>
    <li>Pour respecter une obligation légale</li>
    <li>Pour protéger nos droits, notre propriété ou notre sécurité</li>
  </ul>
  <p>Nos partenaires et sous-traitants sont tenus par des obligations de confidentialité strictes.</p>
</div>

<div class="privacy-article">
  <h2><i class="bi bi-6-circle-fill"></i> Vos Droits</h2>
  <p>Conformément aux lois applicables en matière de protection des données, vous disposez des droits suivants :</p>
  <ul>
    <li><strong>Droit d'accès</strong> : obtenir une copie de vos données personnelles</li>
    <li><strong>Droit de rectification</strong> : corriger des données inexactes</li>
    <li><strong>Droit à l'effacement</strong> : demander la suppression de vos données</li>
    <li><strong>Droit d'opposition</strong> : vous opposer au traitement de vos données</li>
    <li><strong>Droit à la portabilité</strong> : recevoir vos données dans un format structuré</li>
  </ul>
  <p>Pour exercer ces droits, contactez-nous à l'adresse : <strong>privacy@mupenda.cd</strong></p>
</div>

<div class="privacy-article">
  <h2><i class="bi bi-7-circle-fill"></i> Cookies et Technologies Similaires</h2>
  <p>Notre site utilise des cookies et technologies similaires pour améliorer votre expérience, analyser le trafic et personnaliser le contenu. Vous pouvez gérer vos préférences de cookies via les paramètres de votre navigateur.</p>
  <p>Les types de cookies que nous utilisons :</p>
  <ul>
    <li><strong>Cookies essentiels</strong> : nécessaires au fonctionnement du site</li>
    <li><strong>Cookies de performance</strong> : pour analyser l'utilisation du site</li>
    <li><strong>Cookies de fonctionnalité</strong> : pour mémoriser vos préférences</li>
  </ul>
</div>

<div class="privacy-article">
  <h2><i class="bi bi-8-circle-fill"></i> Modifications de la Politique</h2>
  <p>Nous nous réservons le droit de modifier cette politique de confidentialité à tout moment. Les modifications entrent en vigueur dès leur publication sur cette page. Nous vous encourageons à consulter régulièrement cette politique.</p>
  <p>En cas de modifications substantielles, nous vous en informerons par email ou via une notification sur notre site.</p>
</div>"""

        # Create or update CGU
        cgu, created = PageLegale.objects.get_or_create(
            type_page='CGU',
            defaults={
                'titre': "Conditions Générales d'Utilisation",
                'sous_titre': "Veuillez lire attentivement le présent accord, car il contient des informations importantes concernant vos droits et recours légaux.",
                'contenu': cgu_content,
                'derniere_mise_a_jour': timezone.now().date(),
                'est_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Page CGU créée avec succès !'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Page CGU existe déjà.'))

        # Create or update Politique
        politique, created = PageLegale.objects.get_or_create(
            type_page='POLITIQUE',
            defaults={
                'titre': "Politique de Confidentialité",
                'sous_titre': "Nous attachons une grande importance à la protection de vos données personnelles et à votre vie privée.",
                'contenu': politique_content,
                'derniere_mise_a_jour': timezone.now().date(),
                'est_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Page Politique créée avec succès !'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Page Politique existe déjà.'))

        self.stdout.write(self.style.SUCCESS('\n✅ Pages légales initialisées avec succès !'))
