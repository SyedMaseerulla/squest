# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from colorfield.fields import ColorField


class SubscriptionConfig(models.Model):
    mapping_value = models.CharField(_("Mapping Value"), max_length=31, unique=True)
    text_color = ColorField(default='#FFFFFF')
    field_color = ColorField(default='#000000')

    class Meta:
        verbose_name = _("Subscription Config")
        verbose_name_plural = _("Subscription Configs")

    def __str__(self):
        return f"{self.mapping_value} ({self.text_color} {self.field_color})"
