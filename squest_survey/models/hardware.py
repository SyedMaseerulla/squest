# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Hardware(models.Model):
    configuration = models.CharField(_("Configuration"), max_length=63)
    server_name = models.CharField(_("Server Name"), max_length=127)
    availability = models.BooleanField(default=False, verbose_name='Is Available?')
    oneview_hostname = models.CharField(max_length=127)
    remarks = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Hardware")
        verbose_name_plural = _("Hardwares")
        unique_together = ('configuration', 'server_name', 'availability')
        ordering = ('configuration', 'server_name')

    def __str__(self):
        return f"{self.configuration}-{self.server_name}:{self.availability}"

    def is_available(self):
        return self.availability
    is_available.boolean = True
