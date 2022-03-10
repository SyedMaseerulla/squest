# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist

from squest_survey.forms import SO_Form
from service_catalog.models import Instance, OperationType
from squest_survey.models import SO_Question

import logging

LOGGER = logging.getLogger(__name__)


class ScaleOut(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'scale_out.html', {'instances': Instance.objects.all(), 'instance_id': 0})

    def post(self, request, *args, **kwargs):
        # print('ScaleOut post', request.POST)
        instance_id = request.POST.get('instance_select', 0)
        instance = get_object_or_404(Instance, id=instance_id)
        so_forms = []
        error = None
        try:
            so_template = instance.service.operations.get(type=OperationType.SCALEOUT).so_template
            # print('so_template', so_template)
            for category in so_template.categorys.all():
                # print('category', category)
                # print('instance.spec', instance.spec)
                so_form = SO_Form(category=category, instance=instance)
                so_forms.append(so_form)
        except ObjectDoesNotExist:
            LOGGER.error("There is no so_template for %s", instance.name)
            error = f"There is no so_template for {instance.name}"
        context = {
            'instances': Instance.objects.all(),
            'instance_id': instance_id,
            'so_forms': so_forms,
            'error': error,
        }
        return render(request, 'scale_out.html', context)


class ScaleOutRequest(View):

    def post(self, request, *args, **kwargs):
        # print('ScaleOutRequest post', kwargs)
        instance_id = kwargs.get('instance_id', 0)
        instance = get_object_or_404(Instance, id=instance_id)
        print('post', request.POST.keys())
        so_template = instance.service.operations.get(type=OperationType.SCALEOUT).so_template
        for category in so_template.categorys.all():
            for i, question in enumerate(category.questions.all()):
                if question.type == SO_Question.HARDWARE_AVAILABLITY:
                    print("Hardware question")
                    form = SO_Form(request.POST, category=category, instance=instance, user=request.user)
                    if form.is_valid():
                        form.save()
                    else:
                        print(form.errors)
        
        return redirect(reverse('squest_survey:scale-out', kwargs={}))