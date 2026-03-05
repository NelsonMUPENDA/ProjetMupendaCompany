from django.core.management.base import BaseCommand
from MupendaApp.models import Services
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Generate slugs for all services that do not have one'

    def handle(self, *args, **options):
        services_without_slug = Services.objects.filter(slug__isnull=True) | Services.objects.filter(slug='')
        
        count = 0
        for service in services_without_slug:
            service.slug = slugify(service.nom)
            service.save(update_fields=['slug'])
            count += 1
            self.stdout.write(f"Generated slug '{service.slug}' for service '{service.nom}'")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {count} slugs'))
