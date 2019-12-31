import csv
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from booking.forms import MaterialForm, CategoryForm
from booking.models import Material, Category, Event
from users.models import Group


def get_base_context(request):
    return {
        "events": Event.objects.for_user(request.user),
        "groups": Group.objects.filter(type=Group.GROUP),
        "commissions": Group.objects.filter(type=Group.COMMISSION),
    }


def export_materials(request):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="materials.csv"'

    def line_format(mat):
        """

        :param Material mat:
        :return:
        """
        return OrderedDict(
            {
                "ID": mat.id,
                "Type": "simple",
                "Name": mat.name,
                "Published": 1 if mat.lendable else 0,
                "Visibility in catalog": 1 if mat.lendable else 0,
                "Description": mat.description,
                "Regular price": mat.rate_class.rate
                if mat.rate_class is not None
                else "",
                "Categories": [c.name for c in mat.categories.all()]
                if mat.categories.exists()
                else "",
                "Images": [
                    request.build_absolute_uri(i.image.url) for i in mat.images.all()
                ]
                if mat.images.exists()
                else "",
            }
        )

    materials = Material.objects.all()
    writer = csv.DictWriter(response, fieldnames=line_format(materials.first()).keys())
    writer.writeheader()
    for material in materials:
        writer.writerow(line_format(material))

    return response


@login_required
def edit_material(request, id=None):
    """
    View for adding a new material to the database.

    :param request:
    :return:
    """
    material = None
    if id is not None:
        material = Material.objects.get(pk=id)

    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid():
            # Save the model
            return HttpResponseRedirect("/thanks/")
    else:
        if material is not None:
            form = MaterialForm(material)
        else:
            form = MaterialForm()
    return render(
        request,
        "booking/material-editor.html",
        {**get_base_context(request), "form": form},
    )


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

    return render(
        request,
        "booking/event-bookings.html",
        {
            **get_base_context(request),
            "current_event": current_event,
            "current_group": current_group,
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
