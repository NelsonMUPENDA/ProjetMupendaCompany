from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinLengthValidator, RegexValidator
from django.utils import timezone
from MupendaApp.models import Apropos, Formation, Role, Departement, Projet, Tache, CustomUser

User = get_user_model()

class LoginForm(forms.Form):
    """Formulaire de connexion avancé avec validation"""
    username_or_email = forms.CharField(
        label="Nom d'utilisateur ou Email",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-glass',
            'placeholder': 'Entrez votre nom d\'utilisateur ou email',
            'autocomplete': 'username',
            'id': 'username'
        }),
        validators=[
            MinLengthValidator(3, message="L'identifiant doit contenir au moins 3 caractères.")
        ]
    )
    
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-glass',
            'placeholder': 'Entrez votre mot de passe',
            'autocomplete': 'current-password',
            'id': 'password'
        }),
        validators=[
            MinLengthValidator(8, message="Le mot de passe doit contenir au moins 8 caractères.")
        ]
    )
    
    role = forms.ChoiceField(
        label="Rôle d'accès",
        choices=[
            ('', 'Sélectionnez votre rôle'),
            ('SUPER_ADMIN', 'Super Administrateur'),
            ('ADMINISTRATEUR', 'Administrateur'),
            ('CHEF_PROJET', 'Chef de Projet'),
            ('DEVELOPPEUR', 'Développeur'),
            ('DESIGNER', 'Designer'),
            ('COMMERCIAL', 'Commercial'),
            ('COMPTABLE', 'Comptable'),
            ('RH', 'Ressources Humaines'),
            ('SUPPORT', 'Support Technique'),
            ('CLIENT', 'Client'),
            ('COLLABORATEUR', 'Collaborateur'),
            ('FORMATEUR', 'Formateur'),
            ('STAGIAIRE', 'Stagiaire'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control role-select-glass',
            'id': 'role'
        }),
        required=True
    )
    
    remember_me = forms.BooleanField(
        label="Se souvenir de moi",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'rememberMe'
        })
    )
    
    def clean_username_or_email(self):
        """Validation de l'identifiant (email ou username)"""
        username_or_email = self.cleaned_data.get('username_or_email', '').strip()
        
        if not username_or_email:
            raise ValidationError("L'identifiant est obligatoire.")
        
        # Vérification si c'est un email ou un username
        try:
            EmailValidator()(username_or_email)
            # C'est un email
            if not User.objects.filter(email__iexact=username_or_email).exists():
                raise ValidationError("Aucun compte n'est associé à cet email.")
        except ValidationError:
            # C'est un username
            if not User.objects.filter(username__iexact=username_or_email).exists():
                raise ValidationError("Ce nom d'utilisateur n'existe pas.")
        
        return username_or_email
    
    def clean_role(self):
        """Validation du rôle"""
        role = self.cleaned_data.get('role')
        
        if not role:
            raise ValidationError("Veuillez sélectionner un rôle.")
        
        # Vérifier si le rôle existe dans la base de données
        if not Role.objects.filter(nom=role, est_actif=True).exists():
            raise ValidationError("Ce rôle n'est pas valide ou n'est pas actif.")
        
        return role
    
    def clean(self):
        """Validation croisée des champs"""
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')
        role = cleaned_data.get('role')
        
        if username_or_email and password and role:
            # Récupérer l'utilisateur
            try:
                from django.core.validators import validate_email
                try:
                    validate_email(username_or_email)
                    user = User.objects.get(email__iexact=username_or_email)
                except ValidationError:
                    user = User.objects.get(username__iexact=username_or_email)
            except User.DoesNotExist:
                raise ValidationError("Identifiants incorrects.")
            
            # Vérifier si l'utilisateur est banni
            if user.is_banned():
                if user.bloque_jusqua and user.bloque_jusqua > timezone.now():
                    temps_restant = user.bloque_jusqua - timezone.now()
                    minutes = int(temps_restant.total_seconds() / 60)
                    raise ValidationError(f'Compte temporairement bloqué. Réessayez dans {minutes} minutes.')
                else:
                    raise ValidationError('Compte désactivé. Veuillez contacter l\'administrateur.')
            
            # Vérifier si l'utilisateur a le rôle sélectionné
            if not user.user_roles.filter(role__nom=role, est_actif=True).exists():
                raise ValidationError(f'Vous n\'avez pas le rôle {role} ou ce rôle n\'est pas actif.')
        
        return cleaned_data

class UserForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message="Veuillez entrer une adresse email valide.")]
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

class FormationForm(forms.ModelForm):
    """Formulaire pour les formations"""
    class Meta:
        model = Formation
        fields = ['nom', 'slug', 'description', 'image', 'date_debut', 'date_fin', 'heure_debut', 'heure_fin', 'prix', 'formateur', 'categorie', 'status']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'formateur': forms.Select(attrs={'class': 'form-select'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("L'image ne doit pas dépasser 5MB.")
            if not image.content_type.startswith('image/'):
                raise ValidationError("Le fichier doit être une image.")
        return image

class InsertApropos(forms.ModelForm):
    """Formulaire pour modifier les informations de la page À propos"""
    
    class Meta:
        model = Apropos
        fields = [
            # Header
            'titre_page', 'sous_titre_page',
            # Section principale
            'nom_entreprise', 'description_entreprise', 'photo_principale',
            # Statistiques
            'annee_experience', 'label_annee_experience',
            'nombre_projets', 'label_projets',
            'nombre_clients', 'label_clients',
            # Objectifs
            'titre_objectifs', 'icon_objectifs',
            'objectif_1', 'objectif_2', 'objectif_3', 'objectif_4',
            # Valeurs
            'titre_valeurs', 'icon_valeurs',
            'valeur_1', 'valeur_2', 'valeur_3', 'valeur_4',
            # Mission
            'titre_mission', 'icon_mission',
            'mission_1', 'mission_2', 'mission_3', 'mission_4',
            # Configuration
            'titre_section_valeurs', 'est_actif'
        ]
        widgets = {
            'titre_page': forms.TextInput(attrs={'class': 'form-control'}),
            'sous_titre_page': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'description_entreprise': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'photo_principale': forms.FileInput(attrs={'class': 'form-control'}),
            'annee_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'label_annee_experience': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_projets': forms.NumberInput(attrs={'class': 'form-control'}),
            'label_projets': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_clients': forms.NumberInput(attrs={'class': 'form-control'}),
            'label_clients': forms.TextInput(attrs={'class': 'form-control'}),
            'titre_objectifs': forms.TextInput(attrs={'class': 'form-control'}),
            'icon_objectifs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: bi-bullseye'}),
            'objectif_1': forms.TextInput(attrs={'class': 'form-control'}),
            'objectif_2': forms.TextInput(attrs={'class': 'form-control'}),
            'objectif_3': forms.TextInput(attrs={'class': 'form-control'}),
            'objectif_4': forms.TextInput(attrs={'class': 'form-control'}),
            'titre_valeurs': forms.TextInput(attrs={'class': 'form-control'}),
            'icon_valeurs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: bi-heart-fill'}),
            'valeur_1': forms.TextInput(attrs={'class': 'form-control'}),
            'valeur_2': forms.TextInput(attrs={'class': 'form-control'}),
            'valeur_3': forms.TextInput(attrs={'class': 'form-control'}),
            'valeur_4': forms.TextInput(attrs={'class': 'form-control'}),
            'titre_mission': forms.TextInput(attrs={'class': 'form-control'}),
            'icon_mission': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: bi-rocket-takeoff-fill'}),
            'mission_1': forms.TextInput(attrs={'class': 'form-control'}),
            'mission_2': forms.TextInput(attrs={'class': 'form-control'}),
            'mission_3': forms.TextInput(attrs={'class': 'form-control'}),
            'mission_4': forms.TextInput(attrs={'class': 'form-control'}),
            'titre_section_valeurs': forms.TextInput(attrs={'class': 'form-control'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formulaires pour la gestion d'entreprise
class DepartementForm(forms.ModelForm):
    """Formulaire pour la création et modification de départements"""
    
    class Meta:
        model = Departement
        fields = ['nom', 'description', 'responsable', 'couleur', 'est_actif']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du département'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du département'
            }),
            'responsable': forms.Select(attrs={
                'class': 'form-select'
            }),
            'couleur': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control'
            }),
            'est_actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les responsables pour n'afficher que les utilisateurs actifs
        self.fields['responsable'].queryset = CustomUser.objects.filter(
            est_actif=True,
            user_roles__role__nom__in=['SUPER_ADMIN', 'ADMINISTRATEUR', 'CHEF_PROJET']
        ).distinct()

class ProjetForm(forms.ModelForm):
    """Formulaire pour la création et modification de projets"""
    
    class Meta:
        model = Projet
        fields = ['nom', 'description', 'client', 'departement', 'chef_projet', 
                  'statut', 'priorite', 'date_debut', 'date_fin_prevue', 
                  'date_fin_reelle', 'budget', 'progression', 'est_actif']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du projet'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du projet'
            }),
            'client': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du client'
            }),
            'departement': forms.Select(attrs={
                'class': 'form-select'
            }),
            'chef_projet': forms.Select(attrs={
                'class': 'form-select'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priorite': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_fin_prevue': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_fin_reelle': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'progression': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100'
            }),
            'est_actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les chefs de projet
        self.fields['chef_projet'].queryset = CustomUser.objects.filter(
            est_actif=True,
            user_roles__role__nom__in=['SUPER_ADMIN', 'ADMINISTRATEUR', 'CHEF_PROJET']
        ).distinct()
        
        # Filtrer les départements
        self.fields['departement'].queryset = Departement.objects.filter(est_actif=True)

class TacheForm(forms.ModelForm):
    """Formulaire pour la création et modification de tâches"""
    
    class Meta:
        model = Tache
        fields = ['titre', 'description', 'projet', 'assigne_a', 'statut', 
                  'priorite', 'date_echeance', 'temps_estime', 'temps_passe', 'progression']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la tâche'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de la tâche'
            }),
            'projet': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigne_a': forms.Select(attrs={
                'class': 'form-select'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priorite': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_echeance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'temps_estime': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'temps_passe': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'progression': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les projets et les assignés
        self.fields['projet'].queryset = Projet.objects.filter(est_actif=True)
        self.fields['assigne_a'].queryset = CustomUser.objects.filter(est_actif=True)

class UserAdminForm(forms.ModelForm):
    """Formulaire pour la gestion des utilisateurs par l'admin"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'telephone', 
                  'date_embauche', 'photo_profil', 'est_actif']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
            'date_embauche': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'photo_profil': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'est_actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['email'].required = True

class UserRoleForm(forms.Form):
    """Formulaire pour l'assignation des rôles aux utilisateurs"""
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(est_actif=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        empty_label="Sélectionnez un rôle"
    )
    
    date_expiration = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Date d'expiration du rôle (optionnel)"
    )
        
