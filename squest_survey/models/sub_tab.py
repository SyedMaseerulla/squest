# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .sub_template import SubscriptionTemplate


FIELDS_HELP_TEXT = _(
    """Provide a comma-separated list of AWX variable names
    for subscription page, ordering with respect to this list."""
)


TITLES_HELP_TEXT = _(
    """Provide a comma-separated list of titles for fields
    for subscription page, ordering with respect to field list."""
)


def validate_fields(fields):
    values = fields.split(',')
    if len(values) < 1:
        msg = "The selected field requires an associated list of fields."
        msg += " Fields must contain at least one item."
        raise ValidationError(msg)


def validate_titles(fields):
    values = fields.split(',')
    if len(values) < 1:
        msg = "This input field requires an associated list of items."
        msg += " And it must contain at least one item."
        raise ValidationError(msg)


class SubscriptionTab(models.Model):
    sub_templates = models.ManyToManyField(SubscriptionTemplate, verbose_name=_("Subscription Template"), related_name='tabs')
    name = models.CharField(_("Name"), max_length=31)
    fields = models.TextField(_("Fields"), help_text=FIELDS_HELP_TEXT)
    titles = models.TextField(_("Titles"), help_text=TITLES_HELP_TEXT)
    order = models.IntegerField(_("Display Order"))

    class Meta:
        verbose_name = _("Subscription Tab")
        verbose_name_plural = _("Subscription Tabs")
        ordering = ('order',)

    def save(self, *args, **kwargs):
        validate_fields(self.fields)
        validate_titles(self.titles)
        if len(self.get_clean_fields()) != len(self.get_clean_titles()):
            raise ValidationError("Must have same number of fields and titles!")
        super(SubscriptionTab, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))

    def get_clean_fields(self):
        if self.fields is None:
            return []
        fields_list = []
        for choice in self.fields.split(','):
            choice = choice.strip()
            if choice:
                fields_list.append(choice)
        return fields_list

    def get_clean_titles(self):
        if self.titles is None:
            return []
        titles_list = []
        for choice in self.titles.split(','):
            choice = choice.strip()
            if choice:
                titles_list.append(choice)
        return titles_list
