# -*- coding: utf-8 -*-

from django.views.generic import TemplateView

from squest_survey.models import Template, MenuItem, VendorItem


class IndexView(TemplateView):
    template_name = 'vendor_list.html'

    def get_context_data(self, **kwargs):
        menu_item = kwargs.get('menu_item', None)
        context = super(IndexView, self).get_context_data(**kwargs)
        ids = [mi.id for mi in MenuItem.objects.all() if mi.slugify() == menu_item]
        if len(ids) == 1:
            menu_item_id = ids[0]
            menu_item = MenuItem.objects.get(id=menu_item_id)
        context['menu_item'] = menu_item
        context['vendors'] = menu_item.vendors.all()
        return context


class VendorView(TemplateView):
    template_name = 'survey_list.html'

    def get_context_data(self, **kwargs):
        vendor_item = kwargs.get('vendor_item', None)
        context = super(VendorView, self).get_context_data(**kwargs)
        vendor_id = None
        for vi in VendorItem.objects.all():
            if vi.slugify() == vendor_item:
                vendor_id = vi.id
        if vendor_id:
            vendor_item = VendorItem.objects.get(id=vendor_id)
            context['vendor_item'] = vendor_item
            surveys = Template.objects.filter(vendor_item=vendor_item, type=Template.SURVEY)
            context['surveys'] = surveys
        return context
