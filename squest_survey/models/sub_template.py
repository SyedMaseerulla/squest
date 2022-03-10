# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from service_catalog.models import Service


class SubscriptionTemplate(models.Model):
    services = models.ManyToManyField(Service, verbose_name=_("Service"), related_name='sub_templates')
    description = models.TextField(_("Description"))

    class Meta:
        verbose_name = _("Subscription Template")
        verbose_name_plural = _("Subscription Templates")

    def __str__(self):
        return f"{self.description}"
