"""Authentication middleware shared by all protected feature routes."""

from collections.abc import Callable
from typing import cast

from django.contrib.auth import SESSION_KEY, logout
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.shortcuts import render

from accounts.models import User

RequestHandler = Callable[[HttpRequest], HttpResponseBase]


class ActiveAccountMiddleware:
    """End an inactive user's existing session and return a safe 403 page."""

    def __init__(self, get_response: RequestHandler) -> None:
        self.get_response: RequestHandler = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        if self._has_inactive_account(request):
            logout(request)
            return render(request, "403.html", status=403)
        return self.get_response(request)

    def _has_inactive_account(self, request: HttpRequest) -> bool:
        if request.user.is_authenticated:
            return not cast(User, request.user).is_active
        session_user_id: str | None = request.session.get(SESSION_KEY)
        if session_user_id is None:
            return False
        try:
            user_id: int = int(session_user_id)
        except (TypeError, ValueError):
            return False
        return User.objects.filter(pk=user_id, is_active=False).exists()
