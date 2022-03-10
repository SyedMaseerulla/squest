# -*- coding: utf-8 -*-

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .so_template import SO_Template


class SO_Category(models.Model):
    name = models.CharField(_("Name"), max_length=127)
    order = models.IntegerField(_("Display Order"), blank=True, null=True)
    description = models.CharField(_("Description"), max_length=255, blank=True, null=True)
    so_template = models.ManyToManyField(SO_Template, verbose_name=_('Scale Out Template'), related_name='categorys')

    class Meta:
        verbose_name = _('SO Category')
        verbose_name_plural = _('SO Categories')
        ordering = ('order',)

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))
