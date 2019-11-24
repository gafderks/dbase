from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from booking.forms import MaterialForm, CategoryForm
from booking.models import Material, Category


def edit_material(request, id=None):
    """
    View for adding a new material to the database.

    :param request:
    :return:
    """
    material = None
    if id is not None:
        material = Material.objects.get(pk=id)

    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            # Save the model
            return HttpResponseRedirect('/thanks/')
    else:
        if material is not None:
            form = MaterialForm(material)
        else:
            form = MaterialForm()
    return render(request, 'booking/material-editor.html', {'form': form})


def edit_category(request, category_id=None):
    """
    View for adding a new material to the database.

    :param request:
    :return:
    """
    category_list = Category.objects.all()
    page = request.GET.get('page', 1)

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
        return redirect('booking:new_category')

    return render(request, 'booking/category-editor.html', {
        'form': form,
        'categories': categories
    })

def event_bookings(request, event_id):

    return render(request, 'booking/event-bookings.html', {})