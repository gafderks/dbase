from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from booking.filters import MaterialCategoryFilter
from booking.mixins import NavigationMixin
from booking.models import Material


class MaterialListView(LoginRequiredMixin, NavigationMixin, ListView):

    template_name = "catalog/material_list.html"
    model = Material
    paginate_by = 30

    def get_filter(self):
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

    def get_pages(self, context, max_pages=8):
        """

        :param dict context:
        :param int max_pages:
        :return:
        """
        page_no = context.get("page_obj").number
        num_pages = context.get("paginator").num_pages
        max_margin = max_pages // 2

        low = max(page_no - max_margin, 1)
        high = min(page_no + max_margin, num_pages)

        margin_left = page_no - low
        margin_right = high - page_no

        high += max_margin - margin_left
        low -= max_margin - margin_right

        low = max(low, 1)
        high = min(high, num_pages)
        return range(low, high + 1)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filter": self.get_filter(), "pages": self.get_pages(context)})
        return context
