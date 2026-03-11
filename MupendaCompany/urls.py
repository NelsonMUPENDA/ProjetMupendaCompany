from django.contrib import admin
from django.urls import path, include
from MupendaCompany import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('MupendaApp.urls')),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'MupendaApp.views.custom_404_view'
