from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from booking.filters import MaterialCategoryFilter
from booking.mixins import NavigationMixin
from booking.models import Material


def get_pages(context, max_pages=8):
    """
    Limits the number of pages displayed by the paginator to max_pages around the
    current page
    :param dict context: RequestContext
    :param int max_pages: Maximum number of pages to display. Odd numbers are subtracted
     by one due to have an equal amount of numbers on each side of the current page.
     The current page is not part of the maximum.
    :return: range with length maximum 8 + 1 (current page).
    """
    page_no = context.get("page_obj").number
    num_pages = context.get("paginator").num_pages
    max_margin = max_pages // 2

    low = max(page_no - max_margin, 1)
    high = min(page_no + max_margin, num_pages)
    # Compute how many pages are on each side of the current page
    margin_left = page_no - low
    margin_right = high - page_no
    # Add extra pages on a side if the other side is below the maximum.
    high += max_margin - margin_left
    low -= max_margin - margin_right
    # Constrain range to (1, num_pages]
    low = max(low, 1)
    high = min(high, num_pages)
    return range(low, high + 1)


class MaterialListView(LoginRequiredMixin, NavigationMixin, ListView):

    template_name = "catalog/material_list.html"
    model = Material
    paginate_by = 30

    def get_filter(self):
        """
        Returns a filter for filtering the queryset by Category.
        :return FilterSet: MaterialCategoryFilter
        """
        return MaterialCategoryFilter(
            self.request.GET,
            request=self.request,
            queryset=Material.objects.prefetch_related(
                "categories", "images", "attachments"
            ),
            wrapper_class="d-flex justify-content-left flex-wrap mx-n1",
        )

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filter": self.get_filter(), "pages": get_pages(context)})
        return context
