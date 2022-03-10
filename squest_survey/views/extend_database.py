# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from squest_survey.forms import EDB_Form

from service_catalog.models import Instance, OperationType

import logging

LOGGER = logging.getLogger(__name__)


class ExtendDatabase(View):

    def get(self, request, *args, **kwargs):
        # instances = []
        # for instance in Instance.objects.all():
        #     if 'vm_type' in instance.spec and instance.spec['vm_type'] == 'oracle':
        #         if 'db_type' in instance.spec:
        #             if instance.spec['db_type'] == 'non-cdb':
        #                 instances.append(instance)
        return render(request, 'extend_database.html', {'instances': Instance.objects.all(), 'instance_id': 0})

    def post(self, request, *args, **kwargs):
        # print('ExtendDatabase post', request.POST)
        instance_id = request.POST.get('instance_select', 0)
        instance = get_object_or_404(Instance, id=instance_id)
        edb_forms = []
        error = None
        try:
            edb_template = instance.service.operations.get(type=OperationType.EXTEND).edb_template
            for category in edb_template.categorys.all():
                edb_form = EDB_Form(category=category, instance=instance)
                edb_forms.append(edb_form)
        except ObjectDoesNotExist:
            LOGGER.error("There is no edb_template for %s", instance.name)
            error = f"There is no edb_template for {instance.name}"
        except MultipleObjectsReturned:
            LOGGER.error("There are multiple edb_templates associate to %s", instance.name)
            error = f"There are multiple edb_templates associate to {instance.name}"
        context = {
            'instances': Instance.objects.all(),
            'instance_id': instance_id,
            'edb_forms': edb_forms,
            'error': error,
        }
        return render(request, 'extend_database.html', context)


class ExtendDatabaseRequest(View):

    def post(self, request, *args, **kwargs):
        # print('ExtendDatabaseRequest post', request.POST)
        instance_id = kwargs.get('instance_id', 0)
        print(f"ExtendDatabaseRequest {instance_id = }")
        instance = get_object_or_404(Instance, id=instance_id)
        edb_template = instance.service.operations.get(type=OperationType.EXTEND).edb_template
        print("edb_template.categorys",edb_template.categorys.all())
        form = EDB_Form(request.POST, categorys=edb_template.categorys.all(), instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse('squest_survey:extend-database', kwargs={}))
        LOGGER.info("Non valid form: <%s>", form.errors.as_json())
        return ExtendDatabase(request, 'POST', **kwargs)
