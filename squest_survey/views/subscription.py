# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse

from squest_survey.forms import SUB_Form
from squest_survey.models import MenuItem, VendorItem
from squest_survey.models import SubscriptionConfig, LCA_Config
from service_catalog.models import Instance, Operation, OperationType
from guardian.shortcuts import get_objects_for_user

import logging
import json

LOGGER = logging.getLogger(__name__)


class SubscriptionList(View):

    def get(self, request, *args, **kwargs):
        # print('SubscriptionList get', kwargs)
        if vendor_item := kwargs.get('vendor_item', None):
            ids = [mi.id for mi in VendorItem.objects.all() if mi.slugify() == vendor_item]
            if len(ids) == 1:
                vendor_item_id = ids[0]
                vendor_item = VendorItem.objects.get(id=vendor_item_id)
        vendors = VendorItem.objects.all()
        if request.user.is_superuser:
            instances = Instance.objects.all()
        else:
            instances = get_objects_for_user(request.user, 'service_catalog.view_instance')
        context = {
            'instances': instances,
            'vendors': vendors
        }
        return render(request, 'subscription_list.html', context)


class Subscription(View):

    def get(self, request, *args, **kwargs):
        # print('Subscription get', kwargs)
        instance_id = kwargs.get('instance_id', 0)
        instance = get_object_or_404(Instance, id=instance_id)
        sub_panel = None
        sub_tabs = []
        error = None
        # print('instance.spec', instance.spec)
        try:
            # print(f"{instance.service = }")
            # print(f"{instance.service.sub_templates.all() = }")
            sub_template = instance.service.sub_templates.first()
            sub_panel = SUB_Form(panel=sub_template.panels.first(), instance=instance)
            for tab in sub_template.tabs.all():
                # print('tab', tab)
                sub_tab = SUB_Form(tab=tab, instance=instance)
                sub_tabs.append(sub_tab)
        except Exception as ex:
            error = f'{ex}'
            LOGGER.error(error)
        configs = SubscriptionConfig.objects.all()
        operations = []
        for operation in Operation.objects.filter(service=instance.service):
            try:
                lca_config = LCA_Config.objects.get(operation=operation)
                result = lca_config.config_result(instance.spec)
            except LCA_Config.DoesNotExist:
                result = None
            item = {
                'operation': operation,
                'result': result,
            }
            operations.append(item)
        print(f"{operations = }")
        context = {
            'instance': instance,
            'sub_panel': sub_panel,
            'sub_tabs': sub_tabs,
            'error': error,
            'configs': configs,
            'operations': operations,
        }
        return render(request, 'subscription.html', context)
