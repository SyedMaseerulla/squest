# -*- coding: utf-8 -*-

"""
Items of each menu item
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .menu_item import MenuItem
from service_catalog.models import Service

from sorl.thumbnail import get_thumbnail


class VendorItem(models.Model):
    __image = None
    __edb_image = None
    __so_image = None

    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, verbose_name=_("Menu Item"), related_name='vendors')
    name = models.CharField(_("Name"), max_length=31, unique=True)
    image = models.ImageField('Image', upload_to='images', null=True, blank=True)
    order = models.IntegerField(_("Order"))
    services = models.ManyToManyField(Service, verbose_name=_("Service"), related_name='vendors')
    show_edb = models.BooleanField(default=True, verbose_name='Show EDB?')
    edb_image = models.ImageField('EDB Image', upload_to='images', null=True, blank=True)
    show_so = models.BooleanField(default=True, verbose_name='Show SO?')
    so_image = models.ImageField('SO Image', upload_to='images', null=True, blank=True)

    class Meta:
        verbose_name = _("Vendor Item")
        verbose_name_plural = _("Vendor Items")
        ordering = ('menu_item', 'order')
        unique_together = ['menu_item', 'name']

    def slugify(self):
        return slugify(self.name)

    def __str__(self):
        return f"{self.menu_item.name}-{self.order}.{self.name}"

    def save(self, *args, **kwargs):
        super(VendorItem, self).save(*args, **kwargs)
        if self.image and self.image != self.__image:
            self.image = get_thumbnail(self.image, '400x200', quality=100, format='JPEG').name
            self.__image = self.image
            super(VendorItem, self).save(*args, **kwargs)
        if self.edb_image and self.edb_image != self.__edb_image:
            self.edb_image = get_thumbnail(self.edb_image, '400x200', quality=100, format='JPEG').name
            self.__edb_image = self.edb_image
            super(VendorItem, self).save(*args, **kwargs)
        if self.so_image and self.so_image != self.__so_image:
            self.so_image = get_thumbnail(self.so_image, '400x200', quality=100, format='JPEG').name
            self.__so_image = self.so_image
            super(VendorItem, self).save(*args, **kwargs)
