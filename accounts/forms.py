"""Authentication and account-management forms with explicit public inputs."""

from typing import cast

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpRequest, QueryDict
from django.views.decorators.debug import sensitive_variables

from accounts.models import User

CONTROL_CLASSES: str = (
    "h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 "
    "transition-colors hover:border-slate-300 focus:border-accent focus:outline-none "
    "focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500"
)


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


class RegistrationForm(forms.Form):
    """Validate student self-registration inputs and reject unauthorized role assignment."""

    username = UsernameField(
        label="Username",
        max_length=150,
        required=True,
        strip=True,
        validators=[User.username_validator],
        error_messages={"required": "Username cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "register-username",
                "class": CONTROL_CLASSES,
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )
    first_name = forms.CharField(
        label="First name",
        max_length=150,
        required=True,
        strip=True,
        error_messages={"required": "First name cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "register-first-name",
                "class": CONTROL_CLASSES,
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        label="Last name",
        max_length=150,
        required=True,
        strip=True,
        error_messages={"required": "Last name cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "register-last-name",
                "class": CONTROL_CLASSES,
                "autocomplete": "family-name",
            }
        ),
    )
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        required=True,
        error_messages={"required": "Email address cannot be blank."},
        widget=forms.EmailInput(
            attrs={
                "id": "register-email",
                "class": CONTROL_CLASSES,
                "autocomplete": "email",
            }
        ),
    )
    contact_number = forms.CharField(
        label="Contact number (optional)",
        max_length=30,
        required=False,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "id": "register-contact-number",
                "class": CONTROL_CLASSES,
                "autocomplete": "tel",
                "placeholder": "e.g. 0912-345-6789",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        required=True,
        error_messages={"required": "Password cannot be blank."},
        widget=forms.PasswordInput(
            attrs={
                "id": "register-password-1",
                "class": CONTROL_CLASSES,
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        required=True,
        error_messages={"required": "Please confirm your password."},
        widget=forms.PasswordInput(
            attrs={
                "id": "register-password-2",
                "class": CONTROL_CLASSES,
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, data: QueryDict | None) -> None:
        super().__init__(data=data)

    def clean_username(self) -> str:
        username: str = User.normalize_username(self.cleaned_data.get("username", "").strip())
        if not username:
            raise ValidationError("Username cannot be blank.")
        if User.objects.filter(Q(username=username) | Q(email__iexact=username)).exists():
            raise ValidationError("An account with this username already exists.")
        return username

    def clean_email(self) -> str:
        email: str = User.objects.normalize_email(self.cleaned_data.get("email", "").strip())
        if not email:
            raise ValidationError("Email address cannot be blank.")
        if User.objects.filter(Q(email__iexact=email) | Q(username=email)).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self) -> dict[str, object]:
        cleaned_data: dict[str, object] = super().clean()
        password1: str | None = cast(str | None, cleaned_data.get("password1"))
        password2: str | None = cast(str | None, cleaned_data.get("password2"))
        if password1 and password2:
            if password1 != password2:
                self.add_error("password2", "The two passwords do not match.")
            else:
                user_candidate = User(
                    username=str(cleaned_data.get("username") or ""),
                    first_name=str(cleaned_data.get("first_name") or ""),
                    last_name=str(cleaned_data.get("last_name") or ""),
                    email=str(cleaned_data.get("email") or ""),
                )
                try:
                    validate_password(password1, user=user_candidate)
                except ValidationError as error:
                    self.add_error("password1", error)
        return cleaned_data


class ProfileForm(forms.Form):
    """Allow basic users to edit their own name, email, and contact number only."""

    first_name = forms.CharField(
        label="First name",
        max_length=150,
        required=True,
        strip=True,
        error_messages={"required": "First name cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "profile-first-name",
                "class": CONTROL_CLASSES,
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        label="Last name",
        max_length=150,
        required=True,
        strip=True,
        error_messages={"required": "Last name cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "profile-last-name",
                "class": CONTROL_CLASSES,
                "autocomplete": "family-name",
            }
        ),
    )
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        required=True,
        error_messages={"required": "Email address cannot be blank."},
        widget=forms.EmailInput(
            attrs={
                "id": "profile-email",
                "class": CONTROL_CLASSES,
                "autocomplete": "email",
            }
        ),
    )
    contact_number = forms.CharField(
        label="Contact number (optional)",
        max_length=30,
        required=False,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "id": "profile-contact-number",
                "class": CONTROL_CLASSES,
                "autocomplete": "tel",
                "placeholder": "e.g. 0912-345-6789",
            }
        ),
    )

    def __init__(self, data: QueryDict | None, user: User) -> None:
        contact_number: str = (
            getattr(user.profile, "contact_number", "") if hasattr(user, "profile") else ""
        )
        super().__init__(
            data=data,
            initial={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "contact_number": contact_number,
            },
        )
        self.user_id: int = user.pk

    def clean_email(self) -> str:
        email: str = User.objects.normalize_email(self.cleaned_data.get("email", "").strip())
        if not email:
            raise ValidationError("Email address cannot be blank.")
        conflicts = User.objects.filter(Q(email__iexact=email) | Q(username=email)).exclude(
            pk=self.user_id
        )
        if conflicts.exists():
            raise ValidationError("An account with this email already exists.")
        return email
