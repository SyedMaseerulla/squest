# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError

from service_catalog.models import Instance

import logging
import re

LOGGER = logging.getLogger(__name__)


class InstanceNameField(forms.Field):

    def validate(self, value):
        super().validate(value)
        if len(value) < 8:
            LOGGER.debug("Instance name must be at least 8 characters")
            raise ValidationError("Instance name must be at least 8 characters")
        if re.search(r'[^\w_\s]+', value):
            LOGGER.debug("Instance name can only contain alphanumeric characters, underscore and space.")
            raise ValidationError("Instance name can only contain alphanumeric characters, underscore and space.")
        if Instance.objects.filter(name=value).exists():
            LOGGER.debug("Duplicate instance name for %s", value)
            raise ValidationError("The instance name is already in use!")


class RegexField(forms.Field):

    def validate(self, value):
        super().validate(value)
        valid = False
        try:
            regex = self.widget.attrs['regex']
            if re.match(r'' + regex, value):
                res = re.sub(r'' + regex, '', value)
                if len(res) == 0:
                    valid = True
        except Exception as ex:
            LOGGER.debug("Regex error %s", str(ex))
            raise ValidationError("There is an error in regex")
        if not valid:
            LOGGER.debug("Regex does not pass")
            raise ValidationError("Regex does not pass")


class NodesRAC_Field(forms.MultipleChoiceField):

    def validate(self, value):
        super().validate(value)
        if len(value) < 2:
            LOGGER.debug("At least two nodes are required")
            raise ValidationError("At least two nodes are required")
