from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as __
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


def get_all_subcategories(categories):
    """
    Returns the categories as well as their subcategories.
    :param ManyRelatedManager categories: categories to get the descendants of.
    :return list[Category]: list of categories
    """
    all_subcategories = list()
    for category in categories.all():
        all_subcategories.extend(category.get_descendants(include_self=True))
    return all_subcategories


class Category(MPTTModel):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name if self.name else __("[Unnamed category]")

    def get_absolute_url(self):
        return reverse("catalog:catalog") + f"?categories={self.pk}"
