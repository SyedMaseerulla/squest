# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .edb_category import EDB_Category


def validate_choices(choices):
    """Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    values = choices.split(settings.CHOICES_SEPARATOR)
    if len(values) < 1:
        msg = "The selected field requires an associated list of choices."
        msg += " Choices must contain at least one item."
        raise ValidationError(msg)


class EDB_Question(models.Model):

    RADIO = 'radio'
    SELECT = 'select'
    INFOMATION_TEXT = 'infomation-text'
    CALCULATED_FIELD = 'calculated-field'
    EDB_LUN_SIZE = 'edb-lun-size'

    QUESTION_TYPES = (
        (RADIO, _('radio')),
        (SELECT, _('select')),
        (INFOMATION_TEXT, _('text (infomation)')),
        (CALCULATED_FIELD, _('calculated field')),
        (EDB_LUN_SIZE, _('edb lun size')),
    )

    edb_category = models.ForeignKey(EDB_Category, on_delete=models.PROTECT, verbose_name=_('EDB_Category'), related_name='questions')
    display_text = models.CharField(_('Display Text'), max_length=127)
    awx_variable_name = models.CharField(_('AWX Variable Name'), max_length=31, default='awx')
    boolean_response = models.BooleanField(default=False, verbose_name='Is Boolean Response?')
    numeric_response = models.BooleanField(default=False, verbose_name='Is Numeric Response?')
    order = models.IntegerField(_('Display Order'))
    type = models.CharField(_('Type'), max_length=31, choices=QUESTION_TYPES, default=INFOMATION_TEXT)
    choices = models.TextField(_('Choices'), blank=True, null=True)

    class Meta:
        verbose_name = _('EDB Question')
        verbose_name_plural = _('EDB Questions')
        ordering = ('edb_category', 'order')

    def save(self, *args, **kwargs):
        if self.type in [EDB_Question.RADIO, EDB_Question.SELECT]:
            validate_choices(self.choices)
        super(EDB_Question, self).save(*args, **kwargs)

    def get_clean_choices(self):
        """ Return split and stripped list of choices with no null values. """
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(settings.CHOICES_SEPARATOR):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice, allow_unicode=True), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        return 'Question "{}" (*) {}'.format(self.display_text, self.get_clean_choices())
