# -*- coding: utf-8 -*-

"""

"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .lca_operator import LCA_Operator
from service_catalog.models import Operation


class LCA_Config(models.Model):

    START_TYPE = 'START'
    STOP_TYPE = 'STOP'
    EXTEND_TYPE = 'EXTEND'
    SCALEOUT_TYPE = 'SCALEOUT'

    TYPES = (
        (START_TYPE, 'start'),
        (STOP_TYPE, 'stop'),
        (START_TYPE, 'extend'),
        (SCALEOUT_TYPE, 'scaleout'),
    )

    operation = models.OneToOneField(Operation, on_delete=models.PROTECT, primary_key=False, verbose_name=_("Operation"))
    operators = models.ManyToManyField(to='squest_survey.LCA_Operator', verbose_name=_("Operators"))
    # type = models.CharField(_('Type'), max_length=15, choices=TYPES, unique=True)

    class Meta:
        verbose_name = _('LCA Config')
        verbose_name_plural = _('LCA Configs')

    def configuration(self):
        return f"{' '.join([op.field + ':' + op.value + ' ' + str(op.operator) for op in self.operators.all().order_by('order')])}"

    def config_result(self, spec):
        # print(f"config_result {spec = }")
        stack = []
        for operator in self.operators.all().order_by('order'):
            value = spec.get(operator.field, None) 
            if value is not None:
                if isinstance(value, bool):
                    value = str(value).lower()
                stack.append((value == operator.value, operator.operator))
            else:
                return None
        # print(f"config_result {stack = }")
        result, operator = stack.pop()
        while stack:
            item, op = stack.pop()
            if op == LCA_Operator.AND_OP:
                result &= item
            if op == LCA_Operator.OR_OP:
                result |= item
            if op == LCA_Operator.GT_OP:
                result = result > item
            if op == LCA_Operator.LT_OP:
                result = result < item
        if operator == LCA_Operator.ON:
            return result
        elif operator == LCA_Operator.OFF:
            return not result
        else:
            return None

    def __str__(self):
        return self.configuration()
