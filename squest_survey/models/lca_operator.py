# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _


class LCA_Operator(models.Model):

    AND_OP = '&'
    OR_OP = '|'
    GT_OP = '>'
    LT_OP = '<'
    ON = 'ON'
    OFF = 'OFF'

    OPERATORS = (
        (AND_OP, '&'),
        (OR_OP, '|'),
        (GT_OP, '>'),
        (LT_OP, '<'),
        (ON, 'ON'),
        (OFF, 'OFF'),
    )

    field = models.CharField(_("Field"), max_length=31)
    value = models.CharField(_("Value"), max_length=31)
    operator = models.CharField(_("Operator"), max_length=15, choices=OPERATORS)
    order = models.PositiveIntegerField(_("Order"))

    class Meta:
        verbose_name = _("LCA Operator")
        verbose_name_plural = _("LCA Operators")
        ordering = ('order',)

    def __str__(self):
        msg = f"{self.order}.{self.field}:{self.value}-{self.operator}"
        return msg
