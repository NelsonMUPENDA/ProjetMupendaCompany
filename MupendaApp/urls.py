from django.urls import path
from MupendaApp import views

urlpatterns=[
    path('',views.index, name="index"),
    path('inscription/',views.inscription, name="inscription"),
    path('connexion/',views.connexion, name="connexion"),
    path('profil/',views.profil, name="profil"),
    path('deconnexion/',views.deconnexion, name="deconnexion"),
    path('realisations/',views.realisations, name="realisations"),
    path('cgu/',views.cgu, name="conditions_utilisations"),
    path('politique/', views.politique, name="politique"),
    path('formation', views.FormationList.as_view(), name="formation"),
    path('contact/',views.contact, name="contact"),
    path('apropos/',views.apropos, name="apropos"),
    path('faq/',views.faq, name="faq"),
    path('blog/',views.PostList.as_view(), name="blog"),
    path('service/', views.service, name="service"),
    path('blog/<slug:slug>/',views.BlogDetailView.as_view(), name="blog_detail"),
    path('formation/<slug:slug>/',views.FormationDetailView.as_view(), name="detail_formation"),

    # PARTIE D' ADMINISTRATION DU SITE

    path('administration/dashboard/',views.dashboard, name="dashboard"),
    path('administration/indexAdmin/',views.indexAdmin, name="indexAdmin"),
    path('administration/apropos/',views.AdminApropos, name="AdminApropos"),
    path('administration/temoignage/',views.AdminTemoignage, name="AdminTemoignage"),
    path('administration/service/',views.AdminService, name="AdminService"),
    path('administration/edit_service/<str:pk>/',views.EditService, name="edit_service"),
    path('administration/delete_service/<str:pk>/',views.DeleteService, name="delete_service"),
    path('administration/partenaire/',views.AdminPartenaire, name="AdminPartenaire"),
    path('administration/formation/',views.AdminFormation, name="AdminFormation"),
    path('administration/contact/',views.AdminContact, name="AdminContact"),
    path('administration/blog/',views.AdminBlog, name="AdminBlog"),
    path('administration/faq/',views.AdminFaq, name="AdminFaq"),
    path('administration/realisation/',views.AdminRealisation, name="AdminRealisation"),
    path('administration/edit_realisation/<str:pk>/',views.EditRealisation, name="edit_realisation"),
    path('administration/delete_realisation/<str:pk>/',views.DeleteRealisation, name="delete_realisation"),
    path('administration/update_apropos/<int:id_apropos>/',views.UpdateApropos, name="UpdateApropos"),
    
    # FACTURATION
    path('administration/facturation/', views.FacturationView, name='facturation'),
    path('administration/facturation/devis/', views.ListeDevisView, name='liste_devis'),
    path('administration/facturation/devis/ajouter/', views.AjouterDevisView, name='ajouter_devis'),
    path('administration/facturation/devis/<int:devis_id>/', views.FicheDevisView, name='fiche_devis'),
    path('administration/facturation/devis/<int:devis_id>/convertir/', views.ConvertirDevisFactureView, name='convertir_devis_facture'),
    path('administration/facturation/factures/', views.ListeFacturesView, name='liste_factures'),
    path('administration/facturation/factures/<int:facture_id>/', views.FicheFactureView, name='fiche_facture'),
    path('administration/facturation/factures/<int:facture_id>/export-pdf/', views.ExportPDFView, name='export_pdf_facture'),
    
    # COLLABORATEURS
    path('administration/collaborateurs/', views.ListeCollaborateursView, name='liste_collaborateurs'),
    path('administration/collaborateurs/ajouter/', views.AjouterCollaborateurView, name='ajouter_collaborateur'),
    path('administration/collaborateurs/<int:collaborateur_id>/', views.FicheCollaborateurView, name='fiche_collaborateur'),
    path('administration/collaborateurs/<int:collaborateur_id>/modifier/', views.ModifierCollaborateurView, name='modifier_collaborateur'),
    
    # SUPPORT CLIENT
    path('administration/support/', views.SupportView, name='support'),
    path('administration/support/tickets/', views.ListeTicketsView, name='liste_tickets'),
    path('administration/support/tickets/ajouter/', views.AjouterTicketView, name='ajouter_ticket'),
    path('administration/support/tickets/<int:ticket_id>/', views.FicheTicketView, name='fiche_ticket'),
    path('administration/support/tickets/<int:ticket_id>/assigner/', views.AssignerTicketView, name='assigner_ticket'),
    path('administration/support/tickets/<int:ticket_id>/resoudre/', views.ResoudreTicketView, name='resoudre_ticket'),
    path('administration/support/tickets/<int:ticket_id>/message/', views.AjouterMessageView, name='ajouter_message_ticket'),
    
    # GESTION CLIENTS
    path('administration/clients/', views.ClientsView, name='clients'),
    path('administration/clients/ajouter/', views.AjouterClientView, name='AjouterClient'),
    path('administration/clients/<int:client_id>/', views.FicheClientView, name='fiche_client'),
    path('administration/clients/<int:client_id>/modifier/', views.ModifierClientView, name='modifier_client'),
    path('administration/clients/<int:client_id>/supprimer/', views.SupprimerClientView, name='supprimer_client'),
    
    # URLS MANQUANTES
    path('administration/', views.AdministrationView, name='administration'),
    path('administration/temps/', views.TempsView, name='temps'),
    path('administration/projets/', views.AdministrationView, name='AdminProjets'), 
]