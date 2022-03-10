# -*- coding: utf-8 -*-

from django import forms
from django.db.models.query_utils import Q
from django.forms import models
from django.core.exceptions import ValidationError

from squest_survey.models import Answer, Question, Response, EDB_Question, SO_Question
from squest_survey.models import SubscriptionConfig, Hardware, Patch, Recovery_tasks
from squest_survey.signals import survey_completed
from squest_survey.form_fields import InstanceNameField, RegexField, NodesRAC_Field
from squest_survey.utils import get_survey_var_list
from squest_survey.utils import check_and_get_from_spec, check_Key
from service_catalog.models import Request, Instance, Operation, OperationType

from guardian.models import UserObjectPermission
from prettyjson import PrettyJSONWidget

import logging
import json
from ast import literal_eval

LOGGER = logging.getLogger(__name__)


def is_json_object(value):
    if not value:
        return False
    try:
        if isinstance(value, dict):
            json.loads(json.dumps(value))
            return True
        if isinstance(value, list):
            for obj in value:
                json.loads(json.dumps(obj))
            return True
        return False
    except Exception as ex:
        print(f"NOT a valid JSON {value} {ex}")
        return False


class EDB_Form(forms.Form):

    FIELDS = {
        EDB_Question.INFOMATION_TEXT: forms.CharField,
        EDB_Question.CALCULATED_FIELD: forms.CharField,
        EDB_Question.EDB_LUN_SIZE: forms.IntegerField,
    }

    WIDGETS = {
        EDB_Question.RADIO: forms.RadioSelect,
        EDB_Question.SELECT: forms.Select(attrs={'class': 'form-control'}),
        EDB_Question.INFOMATION_TEXT: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        EDB_Question.CALCULATED_FIELD: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        EDB_Question.EDB_LUN_SIZE: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
    }

    def __init__(self, *args, **kwargs):
        """ Expects a survey object to be passed in initially """
        # print('EDB_Form', kwargs)
        categorys = kwargs.pop('categorys', None)
        self.category = kwargs.pop('category', None)
        self.squest_instance = kwargs.pop('instance')
        self.user = kwargs.pop('user', None)
        print("categorys",categorys)
        super(EDB_Form, self).__init__(*args, **kwargs)
        if categorys:
            self.category = categorys.last()
            for category in categorys:
                self.add_questions(category)
        else:
            self.add_questions(self.category)

    def add_questions(self, category):
        for question in category.questions.all():
            # print('add_questions', question)
            kwargs = {'label': question.display_text, 'required': category.extended and question.type != Question.CALCULATED_FIELD}
            initial = self.get_question_initial(question)
            if initial:
                kwargs['initial'] = initial
            choices = self.get_question_choices(question)
            if choices:
                kwargs['choices'] = choices
            widget = self.get_question_widget(question)
            if widget:
                kwargs['widget'] = widget
            field = self.get_question_field(question, **kwargs)

            if category.extended:
                question_id = 'extend_question_%d' % question.pk
            else:
                question_id = 'question_%d' % question.pk

            self.fields[question_id] = field
            self.fields.update({question_id: field})

    def get_question_initial(self, question):
        if question.type == EDB_Question.EDB_LUN_SIZE:
            return self.squest_instance.spec.get('lun_size', '0')
        if self.category.extended and question.type == EDB_Question.SELECT:
            return None
        return self.squest_instance.spec.get(question.awx_variable_name, None)

    def get_question_choices(self, question):
        qchoices = None
        if question.type in [EDB_Question.SELECT, EDB_Question.RADIO]:
            qchoices = question.get_choices()
            if question.type == EDB_Question.SELECT:
                qchoices = tuple([('', '-------------')]) + qchoices
        return qchoices

    def get_question_widget(self, question):
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    def get_question_field(self, question, **kwargs):
        try:
            return self.FIELDS[question.type](**kwargs)
        except KeyError:
            return forms.ChoiceField(**kwargs)

    def save(self, commit=False):
        dct1 = dict()
        survey_var_list = []
        survey_var_list = get_survey_var_list(self.squest_instance.service.operations.get(type=OperationType.EXTEND).job_template.survey)
        for field_name, field_value in list(self.cleaned_data.items()):
            # print('save', field_name)
            if field_name.startswith('extend_question_'):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in
                # the field name in the __init__ method of this form class.
                q_id = int(field_name.split('_')[2])
                question = EDB_Question.objects.get(pk=q_id)
                if(question.boolean_response):
                    if field_value.lower() == "true":
                        dct1[question.awx_variable_name]=True
                    else:
                        dct1[question.awx_variable_name]=False
                elif(question.numeric_response):
                    if field_value is not None and field_value != "":
                        dct1[question.awx_variable_name]=int(field_value)
                elif question.type == EDB_Question.CALCULATED_FIELD:
                    pass
                else:
                    dct1[question.awx_variable_name] = field_value
        for var_name in survey_var_list:
            if not check_Key(dct1, var_name):
                present, value = check_and_get_from_spec(var_name, self.squest_instance.spec)
                if present:
                    dct1[var_name] = value
                else:
                    raise forms.ValidationError('Extras var is missing.', var_name)
        Request.objects.create(instance=self.squest_instance, operation=self.squest_instance.service.operations.get(type=OperationType.EXTEND), state="ACCEPTED", fill_in_survey=dct1, user=self.user)


class SO_Form(forms.Form):
    FIELDS = {
         SO_Question.READONLY_TEXT: forms.CharField
    }

    WIDGETS = {
         SO_Question.HARDWARE_AVAILABLITY: forms.Select(attrs={'class': 'form-control'}),
         SO_Question.READONLY_TEXT: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    }

    def __init__(self, *args, **kwargs):
        """ Expects a survey object to be passed in initially """
        # print('SO_Form', kwargs)
        self.category = kwargs.pop('category')
        self.instance = kwargs.pop('instance')
        self.user = kwargs.pop('user', None)
        super(SO_Form, self).__init__(*args, **kwargs)
        if self.category:
            self.add_questions()

    def add_questions(self):
        for question in self.category.questions.all():
            # print('add_questions', question)
            kwargs = {'label': question.display_text, 'required': False}
            if initial := self.instance.spec.get(question.awx_variable_name, None):
                kwargs['initial'] = initial
            if question.type == SO_Question.HARDWARE_AVAILABLITY:
                if choices := self.get_question_choices(question):
                    print("choices",choices)
                    kwargs['choices'] = choices
            if question.type == SO_Question.HARDWARE_AVAILABLITY:
                kwargs['widget'] = forms.Select(attrs={'class': 'form-control'})
            else:
                kwargs['widget'] = forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
            if question.type == SO_Question.HARDWARE_AVAILABLITY:
                field = forms.ChoiceField(**kwargs)
            else:
                field = forms.CharField(**kwargs)
            question_id = 'question_%d' % question.pk
            self.fields[question_id] = field
            self.fields.update({question_id: field})
    
    def get_question_choices(self, question):
        """Return the choices we should use for a question.
        :param Question question: The question
        :rtype: List of String or None"""
        qchoices = None
        if question.type == SO_Question.HARDWARE_AVAILABLITY:
            qchoices = self.get_hardware_availability_choices()
            # print(f"{self.get_hardware_availability_choices() = }")
        return qchoices
    
    def get_hardware_availability_choices(self):
        hardwares = Hardware.objects.filter(availability=True).values('configuration').order_by().distinct()
        choices_list = []
        for idx, hardware in enumerate(hardwares):
            choices_list.append((hardware['configuration'], hardware['configuration']))
        return tuple([('', '-------------')]) + tuple(choices_list)

    def save(self, commit=False):
        dct1 = dict()
        print("Hi", self.cleaned_data.items())
        for field_name, field_value in list(self.cleaned_data.items()):
            print("so fieldvalue",field_value)
            q_id = int(field_name.split('_')[1])
            question = SO_Question.objects.get(pk=q_id)
            if question.type == SO_Question.HARDWARE_AVAILABLITY:
                hardware = Hardware.objects.filter(availability=True, configuration=field_value).last()
                dct1[question.awx_variable_name] = [hardware.server_name + ":" + hardware.oneview_hostname]
            
        
        survey_var_list = []
        survey_var_list = get_survey_var_list(self.instance.service.operations.get(type=OperationType.SCALEOUT).job_template.survey)
        for var_name in survey_var_list:
            present, value = check_and_get_from_spec(var_name, self.instance.spec)
            if present:
                dct1[var_name] = value
            else:
                raise forms.ValidationError('Extras var is missing.', var_name)
        Request.objects.create(instance=self.instance, operation=self.instance.service.operations.get(type=OperationType.SCALEOUT), state="ACCEPTED", fill_in_survey=dct1, user=self.user)


class SUB_Form(forms.Form):

    def __init__(self, *args, **kwargs):
        """ Expects a survey object to be passed in initially """
        # print('SUB_Form', kwargs)
        self.squest_instance = kwargs.pop('instance', None)
        self.panel = kwargs.pop('panel', None)
        self.tab = kwargs.pop('tab', None)
        super(SUB_Form, self).__init__(*args, **kwargs)
        source = None
        if self.tab:
            source = self.tab
        if self.panel:
            source = self.panel
        if source:
            self.add_questions(source)

    def add_questions(self, source):
        for i, item in enumerate(zip(source.get_clean_fields(), source.get_clean_titles())):
            field, title = item
            kwargs = {'label': title, 'required': False}
            widget_class = 'form-control'
            if initial := self.squest_instance.spec.get(field, None):
                if is_json_object(initial):
                    kwargs['initial'] = json.dumps(initial, indent=2)
                else:
                    kwargs['initial'] = initial
                    if config := SubscriptionConfig.objects.filter(mapping_value=initial).first():
                        widget_class += f" sub-{config.mapping_value}-class"
            if is_json_object(initial):
                kwargs['widget'] = PrettyJSONWidget(attrs={'class': 'form-control jsonwidget', 'readonly': 'readonly'})
            else:
                if len(str(initial)) > 50:
                    kwargs['widget'] = forms.Textarea(attrs={'class': widget_class, 'readonly': 'readonly'})
                else:
                    kwargs['widget'] = forms.TextInput(attrs={'class': widget_class, 'readonly': 'readonly'})
            field = forms.CharField(**kwargs)
            field_id = 'field_%d' % (i + 1)
            self.fields[field_id] = field
            self.fields.update({field_id: field})
        if self.panel:
            sub_form = self.panel
        else:
            sub_form = self.tab
        # make up questions to be always in 2s
        # print(f"{len(sub_form.fields.split(',')) = }")
        for i in range(2 - len(sub_form.fields.split(',')) % 2):
            field = forms.CharField(label='', widget=forms.HiddenInput(), required=False)
            field_id = 'hiddenfield_%d' % (i + 1)
            self.fields[field_id] = field
            self.fields.update({field_id: field})

    def save(self, commit=False):
        pass


class ResponseForm(models.ModelForm):

    FIELDS = {
        Question.SHORT_TEXT: forms.CharField,
        Question.TEXT: forms.CharField,
        Question.INTEGER: forms.IntegerField,
        Question.PASSWORD: forms.CharField,
        Question.INFOMATION_TEXT: forms.CharField,
        Question.INSTANCE_NAME_VALIDATION: InstanceNameField,
        Question.CALCULATED_FIELD: forms.CharField,
        Question.REGEX_VALIDATION: RegexField,
        Question.READONLY_TEXT: forms.CharField,
        Question.HIDDEN_FIELD: forms.CharField,
        Question.RECOVERY_OBJECT: forms.CharField,
        Question.RECOVERY_POINT: forms.CharField,
        Question.HARDWARE_NODES_AVAILABLITY: forms.MultipleChoiceField,
        Question.HARDWARE_NODES_RAC_AVAILABLITY: NodesRAC_Field,
    }

    WIDGETS = {
        Question.SHORT_TEXT: forms.TextInput(attrs={'class': 'form-control'}),
        Question.TEXT: forms.Textarea(attrs={'class': 'form-control'}),
        Question.INTEGER: forms.NumberInput(attrs={'class': 'form-control'}),
        Question.RADIO: forms.RadioSelect,
        Question.SELECT: forms.Select(attrs={'class': 'form-control'}),
        Question.PASSWORD: forms.PasswordInput(attrs={'class': 'form-control'}),
        Question.INFOMATION_TEXT: forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        Question.INSTANCE_NAME_VALIDATION: forms.TextInput(attrs={'class': 'form-control'}),
        Question.CALCULATED_FIELD: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        Question.REGEX_VALIDATION: forms.TextInput(attrs={'class': 'form-control'}),
        Question.READONLY_TEXT: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        Question.HIDDEN_FIELD: forms.HiddenInput(attrs={'readonly': 'readonly'}),
        Question.HARDWARE_AVAILABLITY: forms.Select(attrs={'class': 'form-control'}),
        Question.PATCH_TYPE_AVAILABLITY: forms.Select(attrs={'class': 'form-control'}),
        Question.PATCH_NAMES: forms.Select(attrs={'class': 'form-control'}),
        Question.HARDWARE_NODES_AVAILABLITY: forms.CheckboxSelectMultiple(),
        Question.HARDWARE_NODES_RAC_AVAILABLITY: forms.CheckboxSelectMultiple(),
	    Question.RECOVERY_TASKS: forms.Select(attrs={'class': 'form-control'}),
        Question.RECOVERY_OBJECT: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        Question.RECOVERY_POINT: forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        Question.DEPROVISION_RAC_SELECT: forms.Select(attrs={'class': 'form-control'}),
        Question.DEPROVISION_RAC_NODES: forms.Select(attrs={'class': 'form-control'}),
    }

    class Meta:
        model = Response
        fields = ()

    def __init__(self, *args, **kwargs):
        """ Expects a survey object to be passed in initially """
        # print('ResponseForm', kwargs)
        self.template = kwargs.pop('template')
        self.user = kwargs.pop('user')
        self.category = kwargs.pop('category', None)
        if self.category != '__all__':
            self.questions = self.template.questions.filter(category=self.category).order_by('order')
        else:
            self.questions = self.template.questions.all()
        self.response = kwargs.pop('response')
        self.actual_request = kwargs.pop('actual_request', False)
        self.operation = kwargs.pop('operation', None)
        self.squest_instance = kwargs.pop('squest_instance', None)
        super(ResponseForm, self).__init__(*args, **kwargs)

        self.seleted_hardware = None
        self.seleted_patch_name = None
        self.seleted_restore_task = None
        self.restore_points = []
        self.seleted_deprov_rac_option = None
        self.deprovision_choices = []
        self.dropdown_selected_option = None
        self.answers = False
        self.add_questions(kwargs.get('data'))

    def add_questions(self, data):
        # add a field for each survey question, corresponding to the question
        # type as appropriate.

        for question in self.questions.all():
            # print('add_questions', question, question.is_cascading())
            if question.is_cascading():
                self._add_cascade_question(question, data)
            else:
                self.add_question(question, data)

    def _add_cascade_question(self, question, data):
        self.add_question(question, data, is_cascading=True)
        answer = self._get_preexisting_answer(question)
        # print('_add_cascade_question', answer)
        if answer:
            # print(question.get_clean_choices(), answer.body)
            if len(answer.body) > 0:
                try:
                    index = int(answer.body)
                    cascade_template = question.cascade_templates.all()[index]
                    # print('cascade_template', cascade_template)
                    for cascade_question in cascade_template.questions.all():
                        # print(cascade_question, cascade_question.is_cascading())
                        if cascade_question.is_cascading():
                            self._add_cascade_question(cascade_question, data)
                        else:
                            self.add_question(cascade_question, data)
                except Exception as e:
                    print('_add_cascade_question', 'Err', e)
                    pass

    def add_question(self, question, data, is_cascading=False):
        """Add a question to the form.
        :param Question question: The question to add.
        :param dict data: The pre-existing values from a post request."""
        kwargs = {'label': question.display_text, 'required': question.required}
        if initial := self.get_question_initial(question, data, is_cascading):
            kwargs['initial'] = initial
        if choices := self.get_question_choices(question):
            kwargs['choices'] = choices
        if widget := self.get_question_widget(question):
            kwargs['widget'] = widget

        if self.response and self.response.type != Response.SURVEY and question.type == Question.INSTANCE_NAME_VALIDATION:
            question.type = Question.SHORT_TEXT
        field = self.get_question_field(question, **kwargs)

        if question.type == Question.REGEX_VALIDATION:
            field.widget.attrs['regex'] = question.regex_text

        if is_cascading or question.type == Question.HARDWARE_AVAILABLITY or question.type == Question.PATCH_TYPE_AVAILABLITY or question.type == Question.RECOVERY_TASKS or question.type == Question.DEPROVISION_RAC_SELECT:
            self.fields['cascade_question_%d' % question.pk] = field
            self.fields.update({
                'cascade_question_%d' % question.pk: field,
            })
        else:
            self.fields['question_%d' % question.pk] = field
            self.fields.update({
                'question_%d' % question.pk: field,
            })

    def _get_preexisting_answers(self):
        """Recover pre-existing answers in database.
        The user must be logged. A Response containing the Answer must exists.
        Will create an attribute containing the answers retrieved to avoid multiple db calls.
        :rtype: dict of Answer or None"""
        if self.answers:
            return self.answers
        if self.response is None:
            self.answers = None
        try:
            answers = Answer.objects.filter(response=self.response).prefetch_related('question')
            self.answers = {answer.question.id: answer for answer in answers.all()}
        except Answer.DoesNotExist:
            self.answers = None
        return self.answers

    def _get_preexisting_answer(self, question):
        """Recover a pre-existing answer in database.
        The user must be logged. A Response containing the Answer must exists.
        :param Question question: The question we want to recover in the response.
        :rtype: Answer or None"""
        answers = self._get_preexisting_answers()
        return answers.get(question.id, None)

    def get_question_initial(self, question, data, is_cascading=False):
        """Get the initial value that we should use in the Form
        :param Question question: The question
        :param dict data: Value from a POST request.
        :rtype: String or None"""
        initial = None
        if question.type not in [Question.INFOMATION_TEXT, Question.READONLY_TEXT, Question.HIDDEN_FIELD,Question.RECOVERY_OBJECT,Question.RECOVERY_POINT]:
            answer = self._get_preexisting_answer(question)
            if answer:
                initial = answer.body
                if question.type in [Question.HARDWARE_NODES_AVAILABLITY, Question.HARDWARE_NODES_RAC_AVAILABLITY]:
                    initial = literal_eval(initial)
            if question.type == Question.HARDWARE_AVAILABLITY:
                self.seleted_hardware = initial
                # print(f'{self.seleted_hardware = }')
            if question.type == Question.PATCH_TYPE_AVAILABLITY:
                self.seleted_patch_name = initial
            if question.type == Question.RECOVERY_TASKS:
                self.seleted_restore_task = initial
                print(f'{self.seleted_restore_task = }')
            if question.type == Question.DEPROVISION_RAC_SELECT:
                self.seleted_deprov_rac_option = initial
                print(f'{self.seleted_deprov_rac_option = }')
            if question.type == Question.DEPROVISION_RAC_NODES:
                self.dropdown_selected_option = initial
                print(f'{self.dropdown_selected_option = }')
        else:
            if question.type == Question.INFOMATION_TEXT:
                initial = question.info_text
            if question.type in [Question.READONLY_TEXT, Question.HIDDEN_FIELD]:
                initial = question.readonly_text
            if question.type == Question.RECOVERY_OBJECT:
                self.get_recovery_object_restore_point()
                if len(self.restore_points) > 2:
                    initial = self.restore_points[0]
                else:
                    initial = ""
            if question.type == Question.RECOVERY_POINT:
                self.get_recovery_object_restore_point()
                if len(self.restore_points) > 2:
                    initial = self.restore_points[1] + "-" +self.restore_points[2]
                else:
                    initial = ""
        if data:
            print(f"get_question_initial {data = }")
            # Initialize the field field from a POST request, if any.
            # Replace values from the database
            if is_cascading or question.type:
                initial = data.get('cascade_question_%d' % question.pk)
            else:
                initial = data.get('question_%d' % question.pk)
        return initial

    def get_question_widget(self, question):
        """Return the widget we should use for a question.
        :param Question question: The question
        :rtype: django.forms.widget or None"""
        try:
            if self.response and self.response.type != Response.SURVEY and question.type == Question.INSTANCE_NAME_VALIDATION:
                return self.WIDGETS[Question.READONLY_TEXT]
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    def get_question_choices(self, question):
        """Return the choices we should use for a question.
        :param Question question: The question
        :rtype: List of String or None"""
        qchoices = None
        if question.type == Question.HARDWARE_AVAILABLITY:
            qchoices = self.get_hardware_availability_choices()
            # print(f"{self.get_hardware_availability_choices() = }")
        if question.type in [Question.HARDWARE_NODES_AVAILABLITY, Question.HARDWARE_NODES_RAC_AVAILABLITY]:
            qchoices = self.get_hardware_nodes_availability_choices()
            # print(f"{self.get_hardware_nodes_availability_choices() = }")
        if question.type == Question.PATCH_TYPE_AVAILABLITY:
            qchoices = self.get_patch_type_availability_choices()
        if question.type == Question.PATCH_NAMES:
            qchoices = self.get_patch_name_availability_choices()
        if question.type == Question.RECOVERY_TASKS:
            qchoices = self.get_recovery_task_availability_choices()
        if question.type == Question.DEPROVISION_RAC_NODES:
            qchoices = self.get_available_nodes_for_deprov()
        if question.type in [Question.SELECT, Question.RADIO, Question.DEPROVISION_RAC_SELECT]:
            qchoices = question.get_choices()
            self.deprovision_choices = question.get_choices()
            # print('get_question_choices', question, question.get_choices())
            # add an empty option at the top so that the user has to explicitly
            # select one of the options
            if question.type == Question.SELECT or question.type == Question.DEPROVISION_RAC_SELECT:
                qchoices = tuple([('', '-------------')]) + qchoices
        return qchoices

    def get_hardware_availability_choices(self):
        hardwares = Hardware.objects.filter(availability=True).values('configuration').order_by().distinct()
        choices_list = []
        for idx, hardware in enumerate(hardwares):
            choices_list.append((idx + 1, hardware['configuration']))
        return tuple([('', '-------------')]) + tuple(choices_list)

    def get_hardware_nodes_availability_choices(self):
        # print('get_hardware_nodes_availability_choices', self.seleted_hardware)
        if not self.seleted_hardware:
            return None
        # print(f"{int(self.seleted_hardware) = }")
        selected_configuration = self.get_hardware_availability_choices()[int(self.seleted_hardware)][1]
        # print(f"{selected_configuration = }")
        hardwares = Hardware.objects.filter(availability=True).filter(configuration=selected_configuration)
        choices_list = []
        for hardware in hardwares:
            choices_list.append((hardware.pk, hardware.server_name))
        return tuple(choices_list)

    def get_patch_type_availability_choices(self):
        patch_types = Patch.objects.values('patch_type').distinct()
        choices_list = []
        for idx, patch_type in enumerate(patch_types):
            choices_list.append((idx + 1, patch_type['patch_type']))
        return tuple([('', '-------------')]) + tuple(choices_list)

    def get_patch_name_availability_choices(self):
        if not self.seleted_patch_name:
            return None
        print(f"{int(self.seleted_patch_name) = }")
        selected_patch_type = self.get_patch_type_availability_choices()[int(self.seleted_patch_name)][1]
        print(f"{selected_patch_type = }")
        patches = Patch.objects.filter(patch_type=selected_patch_type)
        choices_list = []
        for patch in patches:
            choices_list.append((patch.pk, patch.name))
        return tuple(choices_list)
    
    def get_recovery_task_availability_choices(self):
        recovery_tasks = Recovery_tasks.objects.values('recover_task').distinct()
        choices_list = []
        for idx, recovery_task in enumerate(recovery_tasks):
            choices_list.append((idx +1, recovery_task['recover_task']))
        return tuple([('', '-------------')]) + tuple(choices_list)
    
    def get_recovery_object_restore_point(self):
        if not self.seleted_restore_task:
            return None
        print(f"{int(self.seleted_restore_task) = }")
        selected_recovery_point = self.get_recovery_task_availability_choices()[int(self.seleted_restore_task)][1]
        print(f"{selected_recovery_point = }")
        choices_list = selected_recovery_point.split("-")
        self.restore_points = choices_list
        #return choices_list[0]

    def get_available_nodes_for_deprov(self):
        choices_list = []
        for node in self.squest_instance.spec['rac_nodes']:
            choices_list.append((node['uuid'], node['node_hostname']))
        #selected_deprov_option = self.deprovision_choices[int(self.dropdown_selected_option)]
        #print("selected deprov",selected_deprov_option)
        return tuple([('', '-------------')]) + tuple(choices_list)
    def get_question_field(self, question, **kwargs):
        """Return the field we should use in our form.
        :param Question question: The question
        :param **kwargs: A dict of parameter properly initialized in
            add_question.
        :rtype: django.forms.fields"""
        # logging.debug("Args passed to field %s", kwargs)
        try:
            if question.type in [Question.INSTANCE_NAME_VALIDATION, Question.REGEX_VALIDATION]:
                kwargs['required'] = True
            return self.FIELDS[question.type](**kwargs)
        except KeyError:
            return forms.ChoiceField(**kwargs)
            
    # def clean(self):
    #     # data from the form is fetched using super function
    #     super(ResponseForm, self).clean()
    #     print(f"{self.fields = }")
    #     print(f"{self.cleaned_data = }")

    #TO-DO: fix pep8 @Nataraj
    def save(self, commit=False):
        # response 'raw' data as dict (for signal)
        data = {'template_id': self.response.template.id, 'uuid': self.response.uuid, 'responses': []}
        # create an answer object for each question and associate it with this response.
        dct1 = dict()
        survey_instance_name = ""
        hd_idx_arr = []
        survey_var_list = []
        survey_var_list = get_survey_var_list(self.response.template.operation.job_template.survey)
        for field_name, field_value in list(self.cleaned_data.items()):
            q_id = int(field_name.split('_')[-1])
            question = Question.objects.get(pk=q_id)
            value = field_value
            if question.type == Question.HARDWARE_AVAILABLITY:
                if self.seleted_hardware:
                    print("self.seleted_hardware", self.seleted_hardware)
                    selected_configuration = self.get_hardware_availability_choices()[int(self.seleted_hardware)][1]
                    value = selected_configuration
            elif question.type in [Question.HARDWARE_NODES_AVAILABLITY, Question.HARDWARE_NODES_RAC_AVAILABLITY]:
                if self.seleted_hardware:
                    id_arr = [int(id) for id in field_value]
                    value = [Hardware.objects.get(id=id).server_name + ":" + Hardware.objects.get(pk=id).oneview_hostname for id in id_arr]
                    hd_idx_arr = id_arr
            elif question.type == Question.PATCH_NAMES:
                if self.seleted_patch_name:
                    print("self.seleted_patch_name", self.seleted_patch_name)
                    value = Patch.objects.get(id=int(field_value)).patch_file
            elif question.type in [Question.SELECT, Question.RADIO]:
                if value is not None and value != "":
                    value = question.get_clean_choices()[int(field_value)]
            print('save', field_name, field_value)
            if field_name.startswith('question_'):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in
                # the field name in the __init__ method of this form class.
                if question.type == Question.INFOMATION_TEXT:
                    continue
                if question.type in [Question.HARDWARE_NODES_AVAILABLITY, Question.HARDWARE_NODES_RAC_AVAILABLITY]:
                    answer, _ = Answer.objects.get_or_create(question=question, response=self.response)
                else:
                    answer = self._get_preexisting_answer(question)
                    if answer is None:
                        answer = Answer(question=question)
                answer.body = field_value
                data['responses'].append((answer.question.id, answer.body))
                LOGGER.debug("Creating answer for question %d of type %s : %s", q_id, answer.question.type, field_value)
                answer.response = self.response
                answer.save()
                #dct1[question.awx_variable_name] = field_value
                if not question.is_var_not_required:
                    if(question.numeric_response):
                        if value is not None and value != "":
                            dct1[question.awx_variable_name]=int(value)
                    elif(question.boolean_response):
                        if value.lower() == "true":
                            dct1[question.awx_variable_name]=True
                        else:
                            dct1[question.awx_variable_name]=False
                    else:
                        dct1[question.awx_variable_name]=value
                if question.type == Question.DEPROVISION_RAC_NODES:
                    rac_nodes = []
                    delete_nodes = []
                    for node in self.squest_instance.spec['rac_nodes']:
                        if node['uuid'] == value:
                            delete_nodes.append(node)
                            dct1["delete_nodes"] = delete_nodes
                        else:
                            rac_nodes.append(node)
                    dct1["rac_nodes"] = rac_nodes
                if question.type == Question.INSTANCE_NAME_VALIDATION:
                    survey_instance_name = question.awx_variable_name
            if field_name.startswith("cascade_question_"):
                # print(q_id, question)
                answer = self._get_preexisting_answer(question)
                if answer is None:
                    answer = Answer(question=question)
                answer.body = field_value
                data['responses'].append((answer.question.id, answer.body))
                LOGGER.debug("Creating answer for cascade question %d of type %s : %s", q_id, answer.question.type, field_value)
                # print("Creating answer for cascade question %d of type %s : %s", q_id, answer.question.type, field_value)
                answer.response = self.response
                answer.save()
                if not question.is_var_not_required:
                    dct1[question.awx_variable_name] = value
        if self.actual_request:
            if self.template.is_lca():
                # LCA template
                pass
            if self.response.type == Response.ADMIN_ACCEPT:
                # Admin accept request
                self.response.request.state = "ACCEPTED"
                self.response.request.save()
            if self.response.type == Response.NEW_OPERATION:
                # New operation request
                print("NEW_OPERATION", self.squest_instance.id)
                for var_name in survey_var_list:
                    if not check_Key(dct1, var_name):
                        present, value = check_and_get_from_spec(var_name, self.squest_instance.spec)
                        if present:
                            dct1[var_name] = value
                        else:
                            raise forms.ValidationError('Extras var is missing.', var_name)
                self.create_operation = Operation.objects.get(id=self.template.operation.id)
                new_request = Request.objects.create(instance=self.squest_instance, operation=self.create_operation, state="ACCEPTED", fill_in_survey=dct1, user=self.user)
                self.response.request = new_request
            if self.response.type == Response.SURVEY:
                for idx in hd_idx_arr:
                    hdware = Hardware.objects.get(pk=idx)
                    hdware.availability = False
                    hdware.save()
                self.create_operation = Operation.objects.get(id=self.template.operation.id)
                new_service = self.template.operation.service
                new_instance = Instance.objects.create(name=dct1[survey_instance_name], billing_group=None, service=new_service, spoc=self.user)
                
                # UserObjectPermission.objects.assign_perm('change_instance', self.user, obj=new_instance)
                # UserObjectPermission.objects.assign_perm('view_instance', self.user, obj=new_instance)
                new_request = Request.objects.create(instance=new_instance, operation=self.create_operation, state="ACCEPTED", fill_in_survey=dct1, user=self.user)
                self.response.request = new_request
            self.response.save()
        survey_completed.send(sender=Response, instance=self.response, data=data)