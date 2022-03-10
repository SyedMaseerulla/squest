# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Patch(models.Model):
    name = models.CharField(max_length=63)
    patch_file = models.CharField(max_length=200)
    patch_type = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('patch')
        verbose_name_plural = _('patches')