"""Authentication and account-management forms with explicit public inputs."""

from typing import cast

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.db.models import Q
from django.http import HttpRequest, QueryDict
from django.views.decorators.debug import sensitive_variables

from accounts.models import User


class LoginForm(AuthenticationForm):
    """Authenticate an unambiguous username/email without accepting account flags."""

    error_messages: dict[str, str] = {
        "invalid_login": "Invalid username/email or password.",
        "inactive": "Invalid username/email or password.",
    }
    username = UsernameField(
        label="Username or email",
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "class": "h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 transition-colors hover:border-slate-300 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 transition-colors hover:border-slate-300 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500",
            }
        ),
    )

    def __init__(self, request: HttpRequest, data: QueryDict | None) -> None:
        super().__init__(request=request, data=data)
        # AuthenticationForm otherwise limits the field to the username's 150 characters.
        self.fields["username"].max_length = 254
        self.fields["username"].widget.attrs["maxlength"] = 254

    @sensitive_variables()
    def clean(self) -> dict[str, str]:
        identifier: str | None = self.cleaned_data.get("username")
        password: str | None = self.cleaned_data.get("password")
        if identifier is not None and password:
            usernames: tuple[str, ...] = tuple(
                User.objects.filter(
                    Q(username=identifier) | Q(email__iexact=identifier)
                ).values_list("username", flat=True)[:2]
            )
            if len(usernames) != 1:
                # Match Django's password-hash work when rejecting an unknown identity.
                User().set_password(password)
                raise self.get_invalid_login_error()
            user: User | None = cast(
                User | None,
                authenticate(self.request, username=usernames[0], password=password),
            )
            if user is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(user)
            self.user_cache = user
        return self.cleaned_data


class AccountSearchForm(forms.Form):
    """Validate the documented basic-user list filters."""

    q = forms.CharField(
        label="Search",
        required=False,
        max_length=200,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "class": "h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 transition-colors hover:border-slate-300 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500",
                "placeholder": "Username, name, email, or contact number",
            }
        ),
    )
    active = forms.TypedChoiceField(
        label="Status",
        required=False,
        choices=(("", "All statuses"), ("true", "Active"), ("false", "Inactive")),
        coerce={"true": True, "false": False}.get,
        empty_value=None,
        widget=forms.Select(
            attrs={
                "class": "h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 transition-colors hover:border-slate-300 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500"
            }
        ),
    )


class AccountStatusForm(forms.Form):
    """Accept only the CSRF-protected confirmation for a named status action."""
