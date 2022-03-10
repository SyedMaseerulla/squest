from django.conf import settings

from .models import MenuItem, VendorItem


def get_menu_items(request):
    return {'MENUITEMS': MenuItem.objects.all().order_by('order')}


def get_vendor_items(request):
    return {'VENDORITEMS': VendorItem.objects.all().order_by('order')}
