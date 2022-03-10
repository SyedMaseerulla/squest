# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from .question import Question


class Operation(models.Model):

    PLUS = '+'
    MINUS = '-'
    TIMES = '×'
    DIVIDE = '÷'
    EQUAL = '='

    OPERATORS = (
        (PLUS, _('addition')),
        (MINUS, _('subtraction')),
        (TIMES, _('multiplication')),
        (DIVIDE, _('division')),
        (EQUAL, _('equation')),
    )

    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name=_('Question'), related_name='operations')
    operator = models.CharField(_('Operator'), max_length=15, choices=OPERATORS)
    order = models.PositiveIntegerField(_('Order'))

    class Meta:
        verbose_name = _('operation')
        verbose_name_plural = _('operations')
        ordering = ('question__templates', 'order')

    def __str__(self):
        msg = "Question '{}' {}: {}".format(self.question.display_text, self.question.get_clean_choices(), self.operator)
        return msg
