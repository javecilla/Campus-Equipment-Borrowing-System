"""Administrator-only return form and confirmation through native POST submission."""

from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.access import admin_required
from accounts.models import User
from borrowing.models import Loan, RequestStatus
from borrowing.queries import manage_loan_details
from borrowing.return_forms import ReturnFormSet, return_formset
from borrowing.return_services import return_units
from borrowing.services import WorkflowConflict


@require_http_methods(["GET", "POST"])
@admin_required
def return_create(request: HttpRequest, loan_id: int) -> HttpResponse:
    """Confirm selected physical units and recheck all authoritative state on POST."""
    loan: Loan = get_object_or_404(manage_loan_details(), pk=loan_id)
    formset: ReturnFormSet = return_formset(
        request.POST if request.method == "POST" else None, loan_id
    )
    conflict: str = ""
    if (
        not loan.outstanding_quantity
        or loan.closed_at is not None
        or loan.request.status not in (RequestStatus.ISSUED, RequestStatus.PARTIALLY_RETURNED)
    ):
        conflict = "This loan has no units eligible for return."
    elif request.method == "POST" and formset.is_valid():
        try:
            return_units(cast(User, request.user).pk, loan_id, formset.selected_returns())
        except WorkflowConflict as error:
            conflict = str(error)
        except ValidationError as error:
            # Service validation remains authoritative if a caller bypasses forms.
            conflict = "; ".join(error.messages)
        else:
            messages.success(request, f"Selected units were returned on loan #{loan_id}.")
            return redirect("borrowing_manage:loan-detail", loan_id=loan_id)
    return render(
        request,
        "borrowing/manage/return_form.html",
        {"loan": loan, "formset": formset, "conflict": conflict},
        status=409 if conflict else 200,
    )
