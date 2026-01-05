from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from MupendaApp.models import Apropos,Formation

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [ 'username','email','password1','password2', ]
        widgets = {
            'username' : forms.TextInput(attrs={'class': 'form-control'}),
            'email' : forms.EmailInput(attrs={'class': 'form-control'}),
            'password1' : forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2' : forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class InsertApropos(forms.ModelForm):
    class Meta:
        model = Apropos
        fields = ['nom', 'contenus', 'photo']
        widgets = {
            'nom' : forms.TextInput(attrs={'class': 'form-control'}),
            'contenus' : forms.Textarea(attrs={'class': 'form-control', 'rows':5}),
            'photo' : forms.FileInput(attrs={'class': 'form-control'}),
        }

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['nom','description','image','date_debut','date_fin','prix','formateur','categorie','status']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'prix': forms.TextInput(attrs={'class': 'form-control'}),
            'formateur': forms.Select(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }