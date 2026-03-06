from .models import SiteContact


def site_contact(request):
    """
    Context processor pour rendre les informations de contact disponibles
    dans tous les templates.
    """
    try:
        contact = SiteContact.objects.filter(est_actif=True).first()
    except:
        contact = None
    return {
        'site_contact': contact
    }
