from crispy_forms.utils import render_crispy_form
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from rules.contrib.views import permission_required, objectgetter

from booking.forms import BookingForm
from booking.models import Booking


@permission_required("booking.change_booking", fn=objectgetter(Booking, "booking_id"))
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.delete()
    return JsonResponse(
        {
            "success": True,
        }
    )


@login_required
def edit_booking(request, booking_id=None):
    """
    View for adding a new booking to the database.

    :param booking_id:
    :param request:
    :return:
    """
    if booking_id:
        booking = get_object_or_404(Booking, pk=booking_id)
    else:
        booking = Booking(requester=request.user)

    form = BookingForm(request.POST or None, instance=booking)
    if request.POST and form.is_valid():
        # check the permissions
        if not request.user.has_perm("booking.change_booking", booking):
            raise PermissionDenied("User may not edit booking")

        booking = form.save()

        form_html = render_crispy_form(
            BookingForm(instance=booking),
            context=csrf(request),
        )
        booking_html = render_to_string(
            "booking/partials/booking-item.html",
            {
                "booking": booking,
                "form": BookingForm(instance=booking),
                "include_game": bool(request.GET.get("include_game", False)),
                "include_group": bool(request.GET.get("include_group", False)),
            },
            request=request,
        )

        return JsonResponse(
            {
                "success": True,
                "form_html": form_html,
                "booking_html": booking_html,
            }
        )

    form_html = render_crispy_form(form, context=csrf(request))
    return JsonResponse({"success": False, "form_html": form_html})
