"""Authentication forms with explicit public input fields."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class LoginForm(AuthenticationForm):
    """Authenticate username/password without accepting role or account flags."""

    error_messages: dict[str, str] = {
        "invalid_login": "Invalid username or password.",
        "inactive": "Invalid username or password.",
    }
    username = UsernameField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "class": "w-full rounded-lg border border-slate-300 px-3 py-2",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "w-full rounded-lg border border-slate-300 px-3 py-2",
            }
        ),
    )
