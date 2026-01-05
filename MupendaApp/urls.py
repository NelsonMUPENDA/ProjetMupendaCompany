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
    path('<slug:slug>/',views.BlogDetailView.as_view(), name="blog_detail"),
    path('<slug:slug>/',views.FormationDetailView.as_view(), name="detail_formation"),

    # PARTIE D' ADMINISTRATION DU SITE

    path('administration/dashboard/',views.dashboard, name="dashboard"),
    path('administration/indexAdmin/',views.indexAdmin, name="indexAdmin"),
    path('administration/apropos/',views.AdminApropos, name="AdminApropos"),
    path('administration/temoignage/',views.AdminTemoignage, name="AdminTemoignage"),
    path('administration/service/',views.AdminService, name="AdminService"),
    path('administration/edit_service/<str:pk>/',views.EditService, name="edit_service"),
    path('administration/delete_service/<str:pk>/',views.DeleteService, name="delete_service"),
    path('administration/partenaire/',views.AdminPartenaire, name="AdminPartenaire"),
    path('administration/formation/',views.FormationForm, name="AdminFormation"),
    path('administration/formation/',views.AdminFormation, name="AdminFormation"),
    path('administration/contact/',views.AdminContact, name="AdminContact"),
    path('administration/blog/',views.AdminBlog, name="AdminBlog"),
    path('administration/faq/',views.AdminFaq, name="AdminFaq"),
    path('administration/realisation/',views.AdminRealisation, name="AdminRealisation"),
    path('administration/edit_realisation/<str:pk>/',views.EditRealisation, name="edit_realisation"),
    path('administration/delete_realisation/<str:pk>/',views.DeleteRealisation, name="delete_realisation"),
    path('administration/update_apropos/<int:id_apropos>/',views.UpdateApropos, name="UpdateApropos"),
]