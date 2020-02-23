import uuid

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from booking.forms import CategoryForm, GameForm, BookingForm
from booking.models import Category, Event, Game, PartOfDay
from users.models import Group


def get_base_context(request):
    return {
        "events": Event.objects.for_user(request.user),
        "groups": Group.objects.filter(type=Group.GROUP),
        "commissions": Group.objects.filter(type=Group.COMMISSION),
        "parts_of_day": PartOfDay.PART_OF_DAY_CHOICES,
    }


@login_required
def edit_category(request, category_id=None):
    """
    View for adding a new material to the database.

    :param request:
    :return:
    """
    category_list = Category.objects.all()
    page = request.GET.get("page", 1)

    paginator = Paginator(category_list, 20)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    if category_id is not None:
        category = get_object_or_404(Category, pk=category_id)
    else:
        category = None

    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect("booking:new_category")

    return render(
        request,
        "booking/category-editor.html",
        {**get_base_context(request), "form": form, "categories": categories},
    )


@login_required
def event_bookings(request, event_id):
    current_event = get_object_or_404(Event, pk=event_id)
    current_group = request.user.group
    if request.user.has_perm("booking.can_view_others_groups_bookings"):
        current_group = get_object_or_404(
            Group, pk=request.GET.get("group", current_group.id)
        )

    games = {
        day: {
            part_of_day: Game.objects.filter(
                event=current_event,
                group=current_group,
                day=day,
                part_of_day=part_of_day,
            )
            for part_of_day, _ in PartOfDay.PART_OF_DAY_CHOICES
        }
        for day in current_event.days
    }

    return render(
        request,
        "booking/event-bookings.html",
        {
            **get_base_context(request),
            "current_event": current_event,
            "current_group": current_group,
            "empty_game_form": GameForm(
                initial={"event": current_event, "group": current_group}
            ),
            "games": games,
        },
    )


@login_required
def home(request):
    context = get_base_context(request)
    events = context["events"]
    if not events:
        return render(
            request,
            "booking/empty.html",
            {**context, "message": _("There are no open events.")},
        )
    return redirect("booking:event_bookings", event_id=events.latest().id)
