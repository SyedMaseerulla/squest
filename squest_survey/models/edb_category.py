# -*- coding: utf-8 -*-

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .edb_template import EDB_Template


class EDB_Category(models.Model):
    name = models.CharField(_("Name"), max_length=127)
    order = models.IntegerField(_("Display Order"), blank=True, null=True)
    description = models.CharField(_("Description"), max_length=255, blank=True, null=True)
    edb_template = models.ManyToManyField(EDB_Template, verbose_name=_("EDB_Template"), related_name='categorys')
    extended = models.BooleanField(default=False, verbose_name='Is Extended Category?')

    class Meta:
        verbose_name = _("EDB Category")
        verbose_name_plural = _("EDB Categories")
        ordering = ('order',)

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))
