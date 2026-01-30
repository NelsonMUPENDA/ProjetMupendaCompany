from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinLengthValidator, RegexValidator
from MupendaApp.models import Apropos,Formation

User = get_user_model()

class UserForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message="Veuillez entrer une adresse email valide.")]
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email
    
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        widgets = {
            'username' : forms.TextInput(attrs={'class': 'form-control', 'minlength': '3'}),
            'email' : forms.EmailInput(attrs={'class': 'form-control'}),
            'password1' : forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2' : forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': 'Minimum 3 caractères. Lettres, chiffres et @/./+/-/_ uniquement.',
        }

class InsertApropos(forms.ModelForm):
    nom = forms.CharField(
        max_length=255,
        validators=[MinLengthValidator(3, message="Le nom doit contenir au moins 3 caractères.")]
    )
    
    class Meta:
        model = Apropos
        fields = ['nom', 'contenus', 'photo']
        widgets = {
            'nom' : forms.TextInput(attrs={'class': 'form-control'}),
            'contenus' : forms.Textarea(attrs={'class': 'form-control', 'rows': '6'}),
            'photo' : forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("L'image ne doit pas dépasser 5MB.")
            if not photo.content_type.startswith('image/'):
                raise ValidationError("Le fichier doit être une image.")
        return photo

class FormationForm(forms.ModelForm):
    nom = forms.CharField(
        max_length=255,
        validators=[MinLengthValidator(3, message="Le nom doit contenir au moins 3 caractères.")]
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    
    prix = forms.DecimalField(
        min_value=0,
        decimal_places=2
    )
    
    class Meta:
        model = Formation
        fields = ['nom','description','image','date_debut','date_fin','prix','formateur','categorie','status']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '6'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'formateur': forms.Select(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin:
            if date_fin < date_debut:
                raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")
        
        return cleaned_data
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("L'image ne doit pas dépasser 5MB.")
            if not image.content_type.startswith('image/'):
                raise ValidationError("Le fichier doit être une image.")
        return image
        
