from django import forms
from django.contrib.auth.models import User
from .models import Notebook


class RegisterForm(forms.Form):

    full_name = forms.CharField(
        max_length=100
    )

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(
            username=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class LoginForm(forms.Form):

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )


class NotebookForm(forms.ModelForm):

    class Meta:
        model = Notebook

        fields = [
            "name",
            "description",
            "category",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Machine Learning"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder":
                    "Describe what you want to learn..."
                }
            ),

            "category": forms.Select(),
        }