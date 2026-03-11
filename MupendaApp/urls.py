from django.urls import path
from MupendaApp import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    # Pages publiques
    path('', views.index, name="index"),
    path('inscription/', views.inscription, name="inscription"),
    path('connexion/', views.connexion, name="connexion"),
    path('ajax/get-user-roles/', views.get_user_roles_ajax, name="get_user_roles_ajax"),
    path('profil/', views.profil, name="profil"),
    path('profil/update/', views.mon_profil_update, name="mon_profil_update"),
    path('profil/password/', views.mon_profil_password, name="mon_profil_password"),
    path('profil/delete/', views.mon_profil_delete, name="mon_profil_delete"),
    path('profil/message/', views.mon_profil_message, name="mon_profil_message"),
    path('profil/appels-offres/', views.mon_profil_appels_offres, name="mon_profil_appels_offres"),
    path('profil/devis/', views.mon_profil_devis, name="mon_profil_devis"),
    path('profil/devis/<int:devis_id>/', views.voir_devis, name="voir_devis"),
    path('profil/devis/<int:devis_id>/annuler/', views.annuler_devis, name="annuler_devis"),
    path('deconnexion/', views.deconnexion, name="deconnexion"),
    path('realisations/', views.realisations, name="realisations"),
    path('realisations/<slug:slug>/', views.RealisationDetailView.as_view(), name="realisation_detail"),
    path('cgu/', views.cgu, name="conditions_utilisations"),
    path('politique/', views.politique, name="politique"),
    path('formation', views.FormationList.as_view(), name="formation"),
    path('contact/', views.contact, name="contact"),
    path('apropos/', views.apropos, name="apropos"),
    path('faq/', views.faq, name="faq"),
    path('blog/', views.PostList.as_view(), name="blog"),
    path('blog/ajax/load-more/', views.load_more_posts, name="load_more_posts"),
    path('service/', views.service, name="service"),
    path('service/<slug:slug>/', views.service_detail, name="service_detail"),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name="blog_detail"),
    path('formation/<slug:slug>/', views.FormationDetailView.as_view(), name="detail_formation"),

    # RÉINITIALISATION DE MOT DE PASSE - Système basé sur code
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password-reset/new-password/', views.password_reset_new, name='password_reset_new'),
    path('password-reset/resend-code/', views.password_reset_resend_code, name='password_reset_resend_code'),

    # TABLEAUX DE BORD PAR RÔLE
    path('dashboard/super-admin/', views.super_admin_dashboard, name="super_admin_dashboard"),
    path('dashboard/analytics/', views.analytics_center, name="analytics_center"),
    # Redirection: dashboard/admin/ redirige vers super_admin_dashboard (consolidation)
    path('dashboard/admin/', views.super_admin_dashboard, name="dashboard"),
    path('dashboard/employe/', views.employe_dashboard, name="employe_dashboard"),
    path('dashboard/formateur/', views.formateur_dashboard, name="formateur_dashboard"),
    path('dashboard/client/', views.client_dashboard, name="client_dashboard"),
    path('dashboard/collaborateur/', views.collaborateur_dashboard, name="collaborateur_dashboard"),
    path('dashboard/stagiaire/', views.stagiaire_dashboard, name="stagiaire_dashboard"),

    # SUPER ADMIN - PAGES AVANCÉES (utilisées par dashboard/super_admin/base_super_admin.html)
    path('dashboard/super-admin/users/', views.super_admin_manage_users, name="super_admin_manage_users"),
    path('dashboard/super-admin/users/export/', views.export_super_admin_users, name="export_super_admin_users"),
    path('dashboard/super-admin/roles/', views.super_admin_manage_roles, name="super_admin_manage_roles"),
    path('dashboard/super-admin/permissions/', views.super_admin_manage_permissions, name="super_admin_manage_permissions"),
    path('dashboard/super-admin/sessions/', views.sessions_management, name="sessions_management"),
    path('dashboard/super-admin/sessions/<str:session_key>/terminate/', views.terminate_session, name="terminate_session"),
    path('dashboard/super-admin/security/', views.security_dashboard, name="security_dashboard"),
    path('dashboard/super-admin/audit-logs/', views.audit_logs, name="audit_logs"),
    path('dashboard/super-admin/maintenance/', views.maintenance_center, name="maintenance_center"),
    path('dashboard/super-admin/maintenance/action/<str:action_code>/', views.super_admin_maintenance_action, name="super_admin_maintenance_action"),
    path('dashboard/super-admin/notifications/', views.notifications_center, name="notifications_center"),
    path('dashboard/super-admin/notifications/export/', views.super_admin_notifications_export, name="super_admin_notifications_export"),
    path('dashboard/super-admin/notifications/mark-all-read/', views.super_admin_notifications_mark_all_read, name="super_admin_notifications_mark_all_read"),
    path('dashboard/super-admin/notifications/clear-all/', views.super_admin_notifications_clear_all, name="super_admin_notifications_clear_all"),
    path('dashboard/super-admin/notifications/<int:notification_id>/mark-read/', views.super_admin_notification_mark_read, name="super_admin_notification_mark_read"),
    path('dashboard/super-admin/notifications/<int:notification_id>/delete/', views.super_admin_notification_delete, name="super_admin_notification_delete"),
    path('dashboard/super-admin/profile/', views.super_admin_profile, name="super_admin_profile"),
    path('dashboard/super-admin/profile/update/', views.super_admin_profile_update, name="super_admin_profile_update"),
    path('dashboard/super-admin/profile/password/', views.super_admin_password_update, name="super_admin_password_update"),
    path('dashboard/super-admin/profile/preferences/', views.super_admin_preferences_update, name="super_admin_preferences_update"),
    path('dashboard/super-admin/system-parameters/', views.system_parameters, name="system_parameters"),

    # GESTION DES DÉPARTEMENTS
    path('dashboard/departements/', views.gestion_departements, name="gestion_departements"),
    path('dashboard/departements/creer/', views.creer_departement, name="creer_departement"),
    path('dashboard/departements/<int:departement_id>/modifier/', views.modifier_departement, name="modifier_departement"),
    path('dashboard/departements/<int:departement_id>/supprimer/', views.supprimer_departement, name="supprimer_departement"),

    # GESTION DES PROJETS
    path('dashboard/projets/', views.gestion_projets, name="gestion_projets"),
    path('dashboard/projets/creer/', views.creer_projet, name="creer_projet"),
    path('dashboard/projets/<int:projet_id>/', views.detail_projet, name="detail_projet"),
    path('dashboard/projets/<int:projet_id>/modifier/', views.modifier_projet, name="modifier_projet"),
    path('dashboard/projets/<int:projet_id>/supprimer/', views.supprimer_projet, name="supprimer_projet"),

    # GESTION DES TÂCHES
    path('dashboard/taches/', views.gestion_taches, name="gestion_taches"),
    path('dashboard/taches/creer/', views.creer_tache, name="creer_tache"),
    path('dashboard/taches/<int:tache_id>/modifier/', views.modifier_tache, name="modifier_tache"),
    path('dashboard/taches/<int:tache_id>/supprimer/', views.supprimer_tache, name="supprimer_tache"),
    path('dashboard/taches/<int:tache_id>/marquer_terminee/', views.marquer_tache_terminee, name="marquer_tache_terminee"),

    # GESTION DES UTILISATEURS (ADMIN)
    path('dashboard/utilisateurs/', views.gestion_utilisateurs, name="gestion_utilisateurs"),
    path('dashboard/utilisateurs/creer/', views.creer_utilisateur, name="creer_utilisateur"),
    path('dashboard/utilisateurs/<int:user_id>/modifier/', views.modifier_utilisateur, name="modifier_utilisateur"),
    path('dashboard/utilisateurs/<int:user_id>/assigner_role/', views.assigner_role_utilisateur, name="assigner_role_utilisateur"),
    path('dashboard/utilisateurs/<int:user_id>/revoquer_role/<int:user_role_id>/', views.revoquer_role_utilisateur, name="revoquer_role_utilisateur"),
    path('dashboard/utilisateurs/<int:user_id>/toggle_role/<int:user_role_id>/', views.toggle_role_status, name="toggle_role_status"),
    path('dashboard/utilisateurs/<int:user_id>/supprimer/', views.supprimer_utilisateur, name="supprimer_utilisateur"),

    # NOTIFICATIONS
    path('dashboard/notifications/', views.gestion_notifications, name="gestion_notifications"),
    path('dashboard/notifications/<int:notification_id>/marquer_lue/', views.marquer_notification_lue, name="marquer_notification_lue"),
    path('dashboard/notifications/compter_non_lues/', views.compter_notifications_non_lues, name="compter_notifications_non_lues"),
    path('dashboard/notifications/api/recentes/', views.api_notifications_recentes, name="api_notifications_recentes"),
    path('dashboard/notifications/api/tout_marquer_lues/', views.marquer_toutes_notifications_lues, name="marquer_toutes_notifications_lues"),

    # LOGS D'ACTIONS
    path('dashboard/logs/', views.gestion_logs, name="gestion_logs"),
    path('dashboard/logs/export/', views.exporter_logs, name="exporter_logs"),

    # GESTION DES SERVICES - ADMINISTRATION (consolidé dans super-admin)
    path('dashboard/super-admin/services/', views.AdminService, name="AdminService"),
    path('dashboard/super-admin/services/edit/<str:pk>/', views.EditService, name="edit_service"),
    path('dashboard/super-admin/services/delete/<str:pk>/', views.DeleteService, name="delete_service"),
    
    # GESTION DES RÉALISATIONS (consolidé dans super-admin)
    path('dashboard/super-admin/realisations/', views.AdminRealisation, name="AdminRealisation"),
    path('dashboard/super-admin/realisations/edit/<str:pk>/', views.EditRealisation, name="edit_realisation"),
    path('dashboard/super-admin/realisations/delete/<str:pk>/', views.DeleteRealisation, name="delete_realisation"),
    
    # GESTION À PROPOS (consolidé dans super-admin)
    path('dashboard/super-admin/apropos/', views.AdminApropos, name="AdminApropos"),
    path('dashboard/super-admin/apropos/update/<int:id_apropos>/', views.UpdateApropos, name="UpdateApropos"),
    
    # AUTRES GESTIONS (consolidé dans super-admin)
    path('dashboard/super-admin/temoignage/', views.AdminTemoignage, name="AdminTemoignage"),
    path('dashboard/super-admin/partenaire/', views.AdminPartenaire, name="AdminPartenaire"),
    path('dashboard/super-admin/formation/', views.AdminFormation, name="AdminFormation"),
    path('dashboard/super-admin/contact/', views.AdminContact, name="AdminContact"),
    path('dashboard/super-admin/blog/', views.AdminBlog, name="AdminBlog"),
    path('dashboard/super-admin/faq/', views.AdminFaq, name="AdminFaq"),
    
    # ADMINISTRATION INDEX (consolidé dans super-admin)
    path('dashboard/super-admin/index/', views.indexAdmin, name="indexAdmin"),
    path('dashboard/super-admin/temps/', views.TempsView, name="temps"),
    
    # FACTURATION (consolidé dans super-admin)
    path('dashboard/super-admin/facturation/', views.FacturationView, name='facturation'),
    path('dashboard/super-admin/facturation/devis/', views.ListeDevisView, name='liste_devis'),
    path('dashboard/super-admin/facturation/devis/ajouter/', views.AjouterDevisView, name='ajouter_devis'),
    path('dashboard/super-admin/facturation/devis/<int:devis_id>/', views.FicheDevisView, name='fiche_devis'),
    path('dashboard/super-admin/facturation/devis/<int:devis_id>/convertir/', views.ConvertirDevisFactureView, name='convertir_devis_facture'),
    path('dashboard/super-admin/facturation/factures/', views.ListeFacturesView, name='liste_factures'),
    path('dashboard/super-admin/facturation/factures/<int:facture_id>/', views.FicheFactureView, name='fiche_facture'),
    path('dashboard/super-admin/facturation/factures/<int:facture_id>/export-pdf/', views.ExportPDFView, name='export_pdf_facture'),
    
    # COLLABORATEURS (consolidé dans super-admin)
    path('dashboard/super-admin/collaborateurs/', views.ListeCollaborateursView, name='liste_collaborateurs'),
    path('dashboard/super-admin/collaborateurs/ajouter/', views.AjouterCollaborateurView, name='ajouter_collaborateur'),
    path('dashboard/super-admin/collaborateurs/<int:collaborateur_id>/', views.FicheCollaborateurView, name='fiche_collaborateur'),
    path('dashboard/super-admin/collaborateurs/<int:collaborateur_id>/modifier/', views.ModifierCollaborateurView, name='modifier_collaborateur'),
    
    # SUPPORT CLIENT (consolidé dans super-admin)
    path('dashboard/super-admin/support/', views.SupportView, name='support'),
    path('dashboard/super-admin/support/tickets/', views.ListeTicketsView, name='liste_tickets'),
    path('dashboard/super-admin/support/tickets/ajouter/', views.AjouterTicketView, name='ajouter_ticket'),
    path('dashboard/super-admin/support/tickets/<int:ticket_id>/', views.FicheTicketView, name='fiche_ticket'),
    path('dashboard/super-admin/support/tickets/<int:ticket_id>/assigner/', views.AssignerTicketView, name='assigner_ticket'),
    path('dashboard/super-admin/support/tickets/<int:ticket_id>/resoudre/', views.ResoudreTicketView, name='resoudre_ticket'),
    path('dashboard/super-admin/support/tickets/<int:ticket_id>/message/', views.AjouterMessageView, name='ajouter_message_ticket'),
    
    # GESTION CLIENTS (consolidé dans super-admin)
    path('dashboard/super-admin/clients/', views.ClientsView, name='clients'),
    path('dashboard/super-admin/clients/ajouter/', views.AjouterClientView, name='AjouterClient'),
    path('dashboard/super-admin/clients/<int:client_id>/', views.FicheClientView, name='fiche_client'),
    path('dashboard/super-admin/clients/<int:client_id>/modifier/', views.ModifierClientView, name='modifier_client'),
    path('dashboard/super-admin/clients/<int:client_id>/supprimer/', views.SupprimerClientView, name='supprimer_client'), 
    path('dashboard/super-admin/clients/<int:client_id>/export-pdf/', views.export_client_pdf, name='export_client_pdf'), 
    
    # EQUIPEMENTS
    path('dashboard/equipements/', views.liste_equipements, name='liste_equipements'),
    path('dashboard/equipements/creer/', views.creer_equipement, name='creer_equipement'),
    path('dashboard/equipements/<str:pk>/modifier/', views.modifier_equipement, name='modifier_equipement'),
    path('dashboard/equipements/<str:pk>/supprimer/', views.supprimer_equipement, name='supprimer_equipement'),
    
    # FORMATEURS
    path('dashboard/formateurs/', views.liste_formateurs, name='liste_formateurs'),
    path('dashboard/formateurs/creer/', views.creer_formateur, name='creer_formateur'),
    path('dashboard/formateurs/<int:pk>/modifier/', views.modifier_formateur, name='modifier_formateur'),
    path('dashboard/formateurs/<int:pk>/supprimer/', views.supprimer_formateur, name='supprimer_formateur'),
    
    path('newsletter/subscribe/', views.newsletter_subscribe, name="newsletter_subscribe"),
    
    # CATEGORIES
    path('dashboard/categories/', views.liste_categories, name='liste_categories'),
    path('dashboard/categories/creer/', views.creer_categorie, name='creer_categorie'),
    path('dashboard/categories/<int:pk>/modifier/', views.modifier_categorie, name='modifier_categorie'),
    path('dashboard/categories/<int:pk>/supprimer/', views.supprimer_categorie, name='supprimer_categorie'),
]