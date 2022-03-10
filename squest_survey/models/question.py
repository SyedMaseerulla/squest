# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .category import Category
from .template import Template
from .calculation import Calculation


CHOICES_HELP_TEXT = _(
    """The choices field is only used if the question type \
    is 'radio', 'select', or 'select multiple' provide a \
    comma-separated list of options for this question."""
)

INFOMATION_TEXT_HELP_TEXT = _(
    """This field is only used if the question type is \
    'infomation-text', provide a read only text information."""
)

REGEX_FIELD_HELP_TEXT = _(
    """This field is only used if the question type is \
    'regex-field', provide a regex validation."""
)


def validate_choices(choices):
    """Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    values = choices.split(settings.CHOICES_SEPARATOR)
    if len(values) < 1:
        msg = "The selected field requires an associated list of choices."
        msg += " Choices must contain at least one item."
        raise ValidationError(msg)


class Question(models.Model):

    SHORT_TEXT = 'short-text'
    TEXT = 'text'
    RADIO = 'radio'
    SELECT = 'select'
    INTEGER = 'integer'
    PASSWORD = 'password'
    INFOMATION_TEXT = 'infomation-text'
    INSTANCE_NAME_VALIDATION = 'instance-name-validation'
    CALCULATED_FIELD = 'calculated-field'
    REGEX_VALIDATION = 'regex-validation'
    READONLY_TEXT = 'readonly-text'
    HIDDEN_FIELD = 'hidden-field'
    HARDWARE_AVAILABLITY = 'hardware-availablity'
    HARDWARE_NODES_AVAILABLITY = 'hardware-nodes-availablity'
    HARDWARE_NODES_RAC_AVAILABLITY = 'hardware-nodes-rac-availablity'
    PATCH_TYPE_AVAILABLITY = 'patch-type-availablity'
    PATCH_NAMES = 'patch_names'
    RECOVERY_TASKS = 'recovery-tasks'
    RECOVERY_OBJECT = 'recovery-object'
    RECOVERY_POINT = 'recovery-point'
    DEPROVISION_RAC_SELECT = 'deprovision-rac-select'
    DEPROVISION_RAC_NODES = 'deprovision-rac-nodes'

    QUESTION_TYPES = (
        (SHORT_TEXT, _('short text (one line)')),
        (TEXT, _('text (multiple line)')),
        (RADIO, _('radio')),
        (SELECT, _('select')),
        (INTEGER, _('integer')),
        (PASSWORD, _('password')),
        (INFOMATION_TEXT, _('text (infomation)')),
        (INSTANCE_NAME_VALIDATION, _('instance name validation')),
        (CALCULATED_FIELD, _('calculated field')),
        (REGEX_VALIDATION, _('regex validation')),
        (READONLY_TEXT, _('readonly text')),
        (HIDDEN_FIELD, _('hidden field')),
        (HARDWARE_AVAILABLITY, _('hardware availablity')),
        (HARDWARE_NODES_AVAILABLITY, _('hardware nodes availablity')),
        (HARDWARE_NODES_RAC_AVAILABLITY, _('hardware nodes rac availablity')),
        (PATCH_TYPE_AVAILABLITY, _('patch type availablity')),
        (PATCH_NAMES, _('patch names')),
        (RECOVERY_TASKS, _('recovery tasks')),
        (RECOVERY_OBJECT, _('recovery object')),
        (RECOVERY_POINT, _('recovery point')),
        (DEPROVISION_RAC_SELECT, _('deprovision rac select')),
        (DEPROVISION_RAC_NODES, _('deprovision rac nodes')),
    )

    display_text = models.CharField(_('Display Text'), max_length=127)
    awx_variable_name = models.CharField(_('AWX Variable Name'), max_length=127, default='awx')
    is_var_not_required = models.BooleanField(default=False, verbose_name='Don not send this as extra var to awx')
    order = models.IntegerField(_('Order'))
    required = models.BooleanField(_('Required'))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_('Category'), related_name='questions')
    templates = models.ManyToManyField(Template, verbose_name=_('Templates'), related_name='questions')
    type = models.CharField(_('Type'), max_length=31, choices=QUESTION_TYPES, default=SHORT_TEXT)
    choices = models.TextField(_('Choices'), blank=True, null=True, help_text=CHOICES_HELP_TEXT)
    numeric_response = models.BooleanField(default=False, verbose_name='Is Numeric Response?')
    boolean_response = models.BooleanField(default=False, verbose_name='Is Boolean Response?')
    cascade_templates = models.ManyToManyField(Template, verbose_name=_('Cascade Templates'), related_name='cascade_questions', blank=True)
    info_text = models.TextField(_('Info Text'), blank=True, null=True, help_text=INFOMATION_TEXT_HELP_TEXT)
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT, primary_key=False, verbose_name=_('Calculations'), blank=True, null=True)
    regex_text = models.CharField(_('Regular Expression'), max_length=255, blank=True, null=True, help_text=REGEX_FIELD_HELP_TEXT)
    readonly_text = models.CharField(_('Readonly Text Input'), max_length=127, blank=True, null=True)

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ('category', 'order')

    def save(self, *args, **kwargs):
        if self.type in [Question.RADIO, Question.SELECT, Question.DEPROVISION_RAC_SELECT]:
            validate_choices(self.choices)
        super(Question, self).save(*args, **kwargs)

    def is_cascading(self):
        return self.cascade_templates.count() > 0
    is_cascading.boolean = True

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
        for idx, choice in enumerate(self.choices.split(settings.CHOICES_SEPARATOR)):
            if item := choice.strip():
                choices_list.append((idx, item))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        msg = "Question '{}' ".format(self.display_text)
        if self.required:
            msg += "(*) "
        msg += "{}".format(self.get_clean_choices())
        return msg
