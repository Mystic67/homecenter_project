from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User
from django import forms


class MyAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(MyAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'input_name form-control rounded',
            'placeholder': "Nom d'utilisateur"})

        self.fields['password'].widget.attrs.update({
            'class': 'input_name form-control rounded',
            'placeholder': 'Mot de passe'})


class MyLoginView(LoginView):
    authentication_form = MyAuthForm


class MySignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    def __init__(self, *args, **kwargs):
        super(MySignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'input_name form-control rounded',
            'placeholder': "Nom d'utilisateur"})

        self.fields['email'].widget.attrs.update({
            'class': 'input_name form-control rounded',
            'placeholder': 'Adresse e-mail'})

        self.fields['password1'].widget.attrs.update({
            'class': 'input_name form-control rounded',
            'placeholder': 'confimation du mot de passe'})

        self.fields['password2'].widget.attrs.update({
            'class': 'input_name form-control rounded',
            'placeholder': 'Mot de passe'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_superuser']
