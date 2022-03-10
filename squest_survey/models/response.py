# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .template import Template
from service_catalog.models import Request

try:
    from django.conf import settings

    if settings.AUTH_USER_MODEL:
        user_model = settings.AUTH_USER_MODEL
    else:
        user_model = User
except (ImportError, AttributeError):
    user_model = User


class Response(models.Model):
    """
    A Response object is a collection of questions and answers with a unique uuid.
    """

    SURVEY = 'survey'
    ADMIN_ACCEPT = 'admin-accept'
    NEW_OPERATION = 'new-operation'

    TYPES = (
        (SURVEY, _('survey')),
        (ADMIN_ACCEPT, _('admin accept')),
        (NEW_OPERATION, _('new operation')),
    )

    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Update date"), auto_now=True)
    template = models.ForeignKey(Template, on_delete=models.PROTECT, verbose_name=_("Template"), related_name="responses")
    user = models.ForeignKey(user_model, on_delete=models.PROTECT, verbose_name=_("User"), null=True, blank=True)
    uuid = models.CharField(_("Feedback unique identifier"), max_length=36)
    request = models.ForeignKey(Request, on_delete=models.PROTECT, primary_key=False, verbose_name=_('Request'), null=True, blank=True)
    type = models.CharField(_('Type'), max_length=31, choices=TYPES, default=SURVEY)

    class Meta:
        verbose_name = _("Response")
        verbose_name_plural = _("Responses")

    def __str__(self):
        msg = "Response to {} by {} for {}".format(self.template, self.user, self.request)
        msg += " on {}".format(self.created)
        return msg
