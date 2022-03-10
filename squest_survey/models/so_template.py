# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from service_catalog.models import Operation


class SO_Template(models.Model):
    operation = models.OneToOneField(Operation, on_delete=models.PROTECT, primary_key=False, verbose_name=_("Operation"))
    description = models.TextField(_("Description"))

    class Meta:
        verbose_name = _("SO Template")
        verbose_name_plural = _("SO Templates")
        ordering = ('operation',)

    def __str__(self):
        return f"{self.operation}-{self.description}"
