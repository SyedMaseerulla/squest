# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from .so_category import SO_Category


class SO_Question(models.Model):
    HARDWARE_AVAILABLITY = 'hardware-availablity'
    READONLY_TEXT = 'readonly-text'

    QUESTION_TYPES = (
        (HARDWARE_AVAILABLITY, _('hardware availablity')),
        (READONLY_TEXT, _('readonly text'))
    )
    so_category = models.ForeignKey(SO_Category, on_delete=models.PROTECT, verbose_name=_('Scale Out Category'), related_name='questions')
    display_text = models.CharField(_('Display Text'), max_length=127)
    awx_variable_name = models.CharField(_('AWX Variable Name'), max_length=31, default='awx')
    order = models.IntegerField(_('Display Order'))
    type = models.CharField(_('Type'), max_length=31, choices=QUESTION_TYPES, default=READONLY_TEXT)

    class Meta:
        verbose_name = _('SO Question')
        verbose_name_plural = _('SO Questions')
        ordering = ('so_category', 'order')

    def __str__(self):
        return 'Question "{}": {}'.format(self.display_text, self.awx_variable_name)
