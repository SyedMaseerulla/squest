# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from squest_survey.models import Template, Question, Calculation, Operation, SubscriptionTemplate, SubscriptionPanel, LCA_Operator, LCA_Config


class LCA_ConfigForm(forms.ModelForm):
    class Meta:
        model = LCA_Config
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # print('CalculationForm', cleaned_data)
        operators = cleaned_data.get('operators')
        last = True
        for operation in operators.all().order_by('-order'):
            if last:
                last = False
                if operation.operator not in [LCA_Operator.ON, LCA_Operator.OFF]:
                    msg = "Last operator must be ON or OFF"
                    raise ValidationError(msg)
            else:
                if operation.operator in [LCA_Operator.ON, LCA_Operator.OFF]:
                    msg = "Only the last operator can be ON or OFF"
                    raise ValidationError(msg)
        return cleaned_data


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        type = cleaned_data.get('type')
        image = cleaned_data.get('image')
        vendor_item = cleaned_data.get('vendor_item')
        if type != Template.SURVEY:
            if image:
                raise ValidationError('Only survey template should have image.')
            if vendor_item:
                raise ValidationError('Only survey template should have vendor item.')
        return cleaned_data


class CalculationForm(forms.ModelForm):
    class Meta:
        model = Calculation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # print('CalculationForm', cleaned_data)
        operations = cleaned_data.get('operation')
        unit = cleaned_data.get('unit', '')
        operation_templates = operations.first().question.templates.all()
        operation_category = operations.first().question.category
        last = True
        for operation in operations.all().order_by('-order'):
            if set(operation.question.templates.all()) != set(operation_templates):
                msg = "All questions must has the same templates"
                raise ValidationError(msg)
            if operation.question.category != operation_category:
                msg = "All questions must from same category"
                raise ValidationError(msg)
            if last:
                last = False
                if operation.operator != Operation.EQUAL:
                    msg = "Last operator must be equation"
                    raise ValidationError(msg)
            else:
                if operation.operator == Operation.EQUAL:
                    msg = "Only the last operator can be equation"
                    raise ValidationError(msg)
            if operation.question.type in [Question.SELECT, Question.RADIO]:
                if not all([c.replace(unit, '').isnumeric() for c in operation.question.get_clean_choices()]):
                    msg = "There is a question with invalid choices"
                    raise ValidationError(msg)
        return cleaned_data


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # print('QuestionForm', cleaned_data)
        type = cleaned_data.get('type')
        choices = cleaned_data.get('choices')
        info_text = cleaned_data.get('info_text')
        regex_text = cleaned_data.get('regex_text')
        readonly_text = cleaned_data.get('readonly_text')
        cascade_templates = cleaned_data.get('cascade_templates')
        templates = cleaned_data.get('templates')
        if len(templates) > 1:
            for template in templates:
                if template.is_cascading():
                    for question in template.cascade_questions.all():
                        if any(template in templates for template in question.templates.all()):
                            msg = "A question can not exist in a cascade template and a template from the same survey."
                            raise ValidationError(msg)
        if (cascade_templates_length := len(cascade_templates)) > 0:
            if cascade_templates_length != len(choices.split(settings.CHOICES_SEPARATOR)):
                msg = "Must have same number of cascade templates and choices"
                raise ValidationError(msg)
        if type not in [Question.RADIO, Question.SELECT, Question.DEPROVISION_RAC_SELECT]:
            if choices and len(choices) > 0:
                msg = "Only question of radio or select can have Choices"
                raise ValidationError(msg)
        if type == Question.HIDDEN_FIELD:
            if regex_text and len(info_text) > 0:
                msg = "Question of hidden field can not have Info Text"
                raise ValidationError(msg)
            if regex_text and len(regex_text) > 0:
                msg = "Question of hidden field can not have Regex Text"
                raise ValidationError(msg)
        if type == Question.INSTANCE_NAME_VALIDATION:
            if regex_text and len(info_text) > 0:
                msg = "Question of instance name can not have Info Text"
                raise ValidationError(msg)
            if regex_text and len(regex_text) > 0:
                msg = "Question of instance name can not have Regex Text"
                raise ValidationError(msg)
            if readonly_text and len(readonly_text) > 0:
                msg = "Question of instance name can not have Readonly Text"
        if type == Question.INFOMATION_TEXT:
            if regex_text and len(regex_text) > 0:
                msg = "Question of text (infomation) can not have Regex Text"
                raise ValidationError(msg)
            if readonly_text and len(readonly_text) > 0:
                msg = "Question of text (infomation) can not have Readonly Text"
                raise ValidationError(msg)
            if info_text and len(info_text) == 0:
                msg = "Question of text (infomation) must have Info Text"
                raise ValidationError(msg)
        if type == Question.REGEX_VALIDATION:
            if regex_text and len(info_text) > 0:
                msg = "Question of regex field can not have Info Text"
                raise ValidationError(msg)
            if readonly_text and len(readonly_text) > 0:
                msg = "Question of regex field can not have Readonly Text"
                raise ValidationError(msg)
            if info_text and len(regex_text) == 0:
                msg = "Question of regex field must have Regex Text"
                raise ValidationError(msg)
        return cleaned_data


class SubscriptionTemplateForm(forms.ModelForm):
    class Meta:
        model = SubscriptionTemplate
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        services = cleaned_data.get('services')
        for service in services.all():
            if service.sub_templates.count() > 1:
                raise ValidationError('One service cannot have multiple sub_templates.')
        return cleaned_data


class SubscriptionPanelForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPanel
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        sub_templates = cleaned_data.get('sub_templates')
        for sub_template in sub_templates.all():
            if sub_template.panels.count() > 1:
                raise ValidationError('One SubscriptionTemplate cannot have multiple panels.')
        return cleaned_data