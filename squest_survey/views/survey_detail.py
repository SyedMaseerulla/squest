# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.views.generic import View
from django.utils.translation import gettext_lazy as _

from squest_survey.forms import ResponseForm
from squest_survey.models import Template, Category, Question, Response, Answer
from squest_survey.utils import check_extra_vars

from service_catalog.models import Request, RequestState, Instance, Operation

import logging
import uuid

LOGGER = logging.getLogger(__name__)


class SurveyDetail(View):

    def get(self, request, *args, **kwargs):
        return SurveyDetail.survey_detail(request, 'GET', **kwargs)

    def post(self, request, *args, **kwargs):
        return SurveyDetail.survey_detail(request, 'POST', **kwargs)

    @staticmethod
    def get_template_response(request, template, survey_type, request_id=0, user_id=0):
        """Retrieve a pre-existing response in database.
        :rtype: Response or None"""
        response = None
        if request.user.is_authenticated:
            if survey_type == Response.ADMIN_ACCEPT:
                try:
                    if request_id != 0:
                        response = Response.objects.prefetch_related('user', 'template', 'request').get(
                            user=request.user, template=template, type=survey_type, request=request_id
                        )
                    else:
                        response = Response.objects.prefetch_related('user', 'template', 'request').get(
                            user=request.user, template=template, type=survey_type, request__state=RequestState.SUBMITTED
                        )
                    # print('get_template_response ADMIN_ACCEPT return', response)
                except Response.DoesNotExist:
                    LOGGER.debug("No saved response ADMIN_ACCEPT for '%s' for user %s", template, request.user)
                    # print(user_id, template.id)
                    try:
                        user_response = Response.objects.prefetch_related('user', 'template', 'request').get(
                            user=user_id, template=template, request__state=RequestState.SUBMITTED
                        )
                    except Response.DoesNotExist:
                        LOGGER.debug("No saved response Scale Out ADMIN_ACCEPT for '%s' for user %s", template, request.user)
                        user_response = None
                    response = Response.objects.create(uuid=uuid.uuid4(), template=template, user=request.user, type=Response.ADMIN_ACCEPT, request=user_response.request)
                    for answer in user_response.answers.all():
                        Answer.objects.create(response=response, question=answer.question, body=answer.body)
                    # print('get_template_response ADMIN_ACCEPT CREATED return', response)
            else:
                try:
                    response = Response.objects.prefetch_related('user', 'template', 'request').get(
                        user=request.user, template=template, request__isnull=True
                    )
                    # print('get_template_response NOT ADMIN_ACCEPT return', response)
                except Response.DoesNotExist:
                    LOGGER.debug("No saved response NOT ADMIN_ACCEPT for '%s' for user %s", template, request.user)
                    response = Response.objects.create(uuid=uuid.uuid4(), template=template, user=request.user, type=survey_type)
        return response

    @staticmethod
    def get_survey_variables(request, **kwargs):
        request_id = kwargs.get('request_id', 0)
        user_id = kwargs.get('user_id', 0)
        operation_id = kwargs.get('operation_id', 0)
        instance_id = kwargs.get('instance_id', 0)
        instance = operation = None
        if operation_id != 0 and instance_id != 0:
            # new operation request
            instance = get_object_or_404(Instance, id=instance_id)
            operation = get_object_or_404(Operation, id=operation_id)
            template = operation.template
            survey_type = Response.NEW_OPERATION
        elif request_id != 0 and user_id != 0:
            # accept request
            target_request = get_object_or_404(Request, id=request_id)
            template = Template.objects.get(pk=target_request.operation.template.pk)
            survey_type = Response.ADMIN_ACCEPT
        else:
            # survey request
            template = Template.objects.get(id=kwargs.get('id'))
            survey_type = Response.SURVEY
        # print('get_template_response', request.user.id, user_id, template.id, survey_type)
        response = SurveyDetail.get_template_response(request, template, survey_type, request_id, user_id)
        ids = {
            'request_id': request_id,
            'user_id': user_id,
            'operation_id': operation_id,
            'instance_id': instance_id,
        }
        return template, response, user_id, instance, operation, ids

    @staticmethod
    def survey_detail(request, get_or_post='GET', **kwargs):
        # print('SurveyDetail', get_or_post, kwargs)
        template, response, user_id, instance, operation, ids = SurveyDetail.get_survey_variables(request, **kwargs)
        print("instance is",ids['instance_id'])
        error = kwargs.get('error', None)            
        calculated_questions = []
        response_forms = []
        if not error:
            if template.type == Template.SURVEY:
                instance_name_qn_count = 0
                for question in template.questions.all():
                    if question.type == Question.INSTANCE_NAME_VALIDATION:
                        instance_name_qn_count += 1
                if instance_name_qn_count == 0:
                    error = _("There is no instance name in the survey.")
                elif instance_name_qn_count > 1:
                    error = _("There are more than one instance name in the survey.")
            if not error:
                categories = set()
                for question in template.questions.all():
                    categories.add(question.category)
                    if question.type == Question.CALCULATED_FIELD:
                        calculated_questions.append(question)
                # print('categories', categories)
                if len(categories) > 0:
                    max_order = max(c.order if c else 0 for c in categories) + 1
                    categories = sorted(categories, key=lambda c: c.order if c else max_order)
                    # print('sorted categories', categories)
                    # print('calculated_questions', calculated_questions)

                # if get_or_post == 'POST':
                #     print('post', request.POST)
                for category in categories:
                    # print(category)
                    if get_or_post == 'GET':
                        print(instance)
                        form = ResponseForm(template=template, response=response, user=request.user, category=category, operation=operation, squest_instance=instance)
                    if get_or_post == 'POST':
                        print(instance)
                        form = ResponseForm(request.POST, response=response, template=template, user=request.user, category=category, operation=operation, squest_instance=instance)
                        if form.is_valid():
                            form.save()
                            response = SurveyDetail.get_template_response(request, template, user_id, operation)
                            form = ResponseForm(response=response, template=template, user=request.user, category=category, operation=operation, squest_instance=instance)
                    if not category:
                        category = Category(name='No category', description='No cat desc', shown=True)
                    response_forms.append({'form': form, 'category': category})
        context = {
            'response_forms': response_forms,
            'template': template,
            'calculated_questions': calculated_questions,
            'ids': ids,
            'instance': instance,
            'operation': operation,
            'error': error,
        }
        return render(request, 'survey.html', context)


class SurveyRequest(View):

    def post(self, request, *args, **kwargs):
        # print('SurveyRequest', 'post', kwargs)
        template, response, _, instance, _, _ = SurveyDetail.get_survey_variables(request, **kwargs)
        error = None
        if response.type != Response.ADMIN_ACCEPT:
            error = check_extra_vars(request, response, request.POST.keys(), instance)
        kwargs['error'] = error
        print('post', request.POST.keys())
        form = ResponseForm(request.POST, template=template, response=response, squest_instance=instance, user=request.user, category='__all__', actual_request=True)
        if form.is_valid() and error is None:
            form.save()
            return redirect(reverse('service_catalog:request_list', kwargs={}))
        LOGGER.info("Non valid form: <%s>", form.errors.as_json())
        return SurveyDetail.survey_detail(request, 'POST', **kwargs)
