# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from .vendor_item import VendorItem

from service_catalog.models import Operation

from sorl.thumbnail import get_thumbnail


class Template(models.Model):
    __image = None

    SURVEY = 'survey'
    CASCADE = 'cascade'
    LCA = 'LCA'

    TEMPLATE_TYPES = (
        (SURVEY, _('Survey')),
        (CASCADE, _('Cascade')),
        (LCA, _('LCA')),
    )

    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), null=True, blank=True)
    operation = models.OneToOneField(Operation, on_delete=models.PROTECT, primary_key=False, verbose_name=_('Operation'), related_name='template', null=True, blank=True)
    type = models.CharField(_('Type'), max_length=31, choices=TEMPLATE_TYPES, default=SURVEY)
    image = models.ImageField('Image', upload_to='images', null=True, blank=True)
    vendor_item = models.ForeignKey(VendorItem, on_delete=models.PROTECT, verbose_name=_('Vendor Item'), null=True, blank=True)

    class Meta:
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ('type', 'operation')

    def __str__(self):
        if self.is_cascading():
            return '{}: {}'.format(self.name, self.description)
        return '{}({})'.format(self.name, self.operation.job_template)

    def save(self, *args, **kwargs):
        super(Template, self).save(*args, **kwargs)
        # print(get_thumbnail(self.image, '400x200', quality=100, format='JPEG'))
        if self.image and self.image != self.__image:
            self.image = get_thumbnail(self.image, '400x200', quality=100, format='JPEG').name
            self.__image = self.image
            super(Template, self).save(*args, **kwargs)

    def is_cascading(self):
        return self.type == Template.CASCADE
    is_cascading.boolean = True

    def is_lca(self):
        return self.type == Template.LCA
    is_lca.boolean = True
