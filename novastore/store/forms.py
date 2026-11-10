from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Ad", max_length=150, widget=forms.TextInput(attrs={"autocomplete": "given-name"}))
    last_name = forms.CharField(label="Soyad", max_length=150, widget=forms.TextInput(attrs={"autocomplete": "family-name"}))
    email = forms.EmailField(label="E-posta adresi", max_length=254, widget=forms.EmailInput(attrs={"autocomplete": "email"}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "username", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresiyle zaten bir hesap oluşturulmuş.")
        return email


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label='Ad soyad', max_length=120)
    address = forms.CharField(label='Örnek teslimat adresi', max_length=500, widget=forms.Textarea(attrs={'rows': 3}))
    token = forms.UUIDField(widget=forms.HiddenInput)
