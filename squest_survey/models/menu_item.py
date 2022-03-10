# -*- coding: utf-8 -*-

"""
Items to be displayed under Database section in sidebar
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class MenuItem(models.Model):
    name = models.CharField(_("Name"), max_length=15, unique=True)
    order = models.IntegerField(_("Order"))

    class Meta:
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        ordering = ('order',)

    def slugify(self):
        return slugify(self.name)

    def __str__(self):
        return f"{self.order}.{self.name}"
