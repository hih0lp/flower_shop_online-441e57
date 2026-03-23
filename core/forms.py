from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Order


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('address', 'phone')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
