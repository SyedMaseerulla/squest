# -*- coding: utf-8 -*-

"""
One calculation consist of multiple operations and the last operation's operator must be '='
The design idea of this implementation is similar to mathematical equation, e.g.
operation 1: qn1, times; operation 2: qn2, addition; operation 3: qn3, equation
qn1 x qn2 + qn3 = result
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Calculation(models.Model):
    operation = models.ManyToManyField(to='squest_survey.Operation', verbose_name=_('Operation'))
    unit = models.CharField(_('Unit'), max_length=15, null=True, blank=True)

    def calculation(self):
        return f"{' '.join([str(op.question.display_text) + ' ' + str(op.operator) for op in self.operation.all()])}"

    def __str__(self):
        return self.calculation()
