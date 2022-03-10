# -*- coding: utf-8 -*-

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    order = models.IntegerField(_("Display order"))
    description = models.CharField(_("Description"), max_length=1023, blank=True, null=True)
    shown = models.BooleanField(default=False, verbose_name='Show DESC?')

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ('order',)

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))
