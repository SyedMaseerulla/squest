# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from squest_survey.models import Template, Category, Question, Calculation, Operation, Response, Answer
from squest_survey.models import MenuItem, VendorItem
from squest_survey.models import EDB_Template, EDB_Category, EDB_Question
from squest_survey.models import SO_Template, SO_Category, SO_Question
from squest_survey.models import SubscriptionTemplate, SubscriptionPanel, SubscriptionTab, SubscriptionConfig
from squest_survey.models import Hardware
from squest_survey.models import LCA_Operator, LCA_Config

from squest_survey.admin_forms import *

from service_catalog.models import Service as SquestService
from service_catalog.models import Operation as SquestOperation


@admin.register(SquestService)
class SquestServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    fields = ('name', 'description')


@admin.register(SquestOperation)
class SquestOperationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type', 'service')
    list_display_links = ('name',)
    exclude = ('enabled_survey_fields', 'auto_accept')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order', 'shown')
    list_display_links = ('name',)


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('question', 'operator', 'order')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'question':
            kwargs['queryset'] = Question.objects.filter(type__in=[Question.INTEGER, Question.SELECT, Question.RADIO]).filter(cascade_templates__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    form = CalculationForm
    list_display = ('calculation', 'unit')
    filter_horizontal = ('operation',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    list_display = ('get_templates', 'display_text', 'category', 'order', 'is_cascading', 'awx_variable_name')
    list_display_links = ('display_text',)
    # list_filter = ('template__name',)
    filter_horizontal = ('templates', 'cascade_templates')
    ordering = ('category', 'order')
    search_fields = ['templates__name']

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'templates':
    #         kwargs['queryset'] = Template.objects.exclude(job_template_id=None)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_templates(self, obj):
        return ', '.join([t.name for t in obj.templates.all()])
    get_templates.short_description = _('Templates')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'cascade_templates':
            kwargs['queryset'] = Template.objects.filter(type=Template.CASCADE)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class IsCascadingFilter(admin.SimpleListFilter):
    title = 'Is Cascading'
    parameter_name = 'is_cascading'

    YES = 'Yes'
    NO = 'No'

    def lookups(self, request, model_admin):
        return (
            (self.YES, _(self.YES)),
            (self.NO, _(self.NO)),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == self.YES:
            return queryset.filter(job_template_id=None)
        elif value == self.NO:
            return queryset.exclude(job_template_id=None)
        return queryset


class IsLCA_Filter(admin.SimpleListFilter):
    title = 'Is LCA'
    parameter_name = 'is_lca'

    YES = 'Yes'
    NO = 'No'

    def lookups(self, request, model_admin):
        return (
            (self.YES, _(self.YES)),
            (self.NO, _(self.NO)),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == self.YES:
            return queryset.filter(type=Template.LCA)
        elif value == self.NO:
            return queryset.exclude(type=Template.LCA)
        return queryset


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    form = TemplateForm
    list_display = ('get_job_template', 'name', 'vendor_item', 'type', 'description', 'preview_image')
    list_display_links = ('name',)
    list_filter = (IsCascadingFilter, IsLCA_Filter)
    ordering = ('-operation__job_template', 'name')

    def get_job_template(self, obj):
        if not obj.operation:
            return None
        return obj.operation.job_template
    get_job_template.short_description = _('Job Template')

    def get_inline_instances(self, request, obj=None):
        return obj and super(TemplateAdmin, self).get_inline_instances(request, obj) or []

    def preview_image(self, obj):
        if obj.is_cascading() or obj.is_lca():
            return 'N.A.'
        if obj.image:
            image_id = 'image_' + str(obj.id)
            return format_html(
                '''
                <img id="{}" style="display:none; position:absolute; top:0px; left:0px; height:calc(200px); width:calc(400px); border:5px solid; z-index:1000;" src="{}" />
                <div style="font-size:18pt; position:relative; cursor:pointer;" onmouseover="document.getElementById('{}').style.display='block'; console.log(this.getBoundingClientRect(), this.parentNode.parentNode.getBoundingClientRect()); document.getElementById('{}').style.left=(this.getBoundingClientRect().left-this.parentNode.parentNode.getBoundingClientRect().x+35)+'px'; var scrollHeight = window.pageYOffset || document.documentElement.scrollTop; console.log(window.pageYOffset, document.documentElement.scrollTop, screen.height, scrollHeight); if (this.getBoundingClientRect().top+200<screen.height-200) document.getElementById('{}').style.top=(scrollHeight+this.getBoundingClientRect().top-298)+'px'; document.getElementById('{}').style.cursor='pointer';" onmouseout="document.getElementById('{}').style.display='none';">📷</div>
                '''.format(image_id, obj.image.url, image_id, image_id, image_id, image_id, image_id, image_id, image_id))
        else:
            return 'No image available'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(TemplateAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['operation'].widget.can_add_related = False
        form.base_fields['operation'].widget.can_delete_related = False
        form.base_fields['operation'].widget.can_change_related = False
        return form


class AnswerBaseInline(admin.StackedInline):
    fields = ('question', 'body')
    readonly_fields = ('question',)
    extra = 0
    model = Answer


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'template', 'type', 'user', 'created')
    list_filter = ('template', 'type', 'created')
    date_hierarchy = 'created'
    inlines = [AnswerBaseInline]
    readonly_fields = ('template', 'created', 'updated', 'uuid', 'user')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'body', 'created', 'updated')
    list_filter = ('response',)
    date_hierarchy = 'created'
    readonly_fields = ('response', 'question', 'created', 'updated')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')


@admin.register(VendorItem)
class VendorItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_item', 'order')
    filter_horizontal = ('services',)


@admin.register(EDB_Template)
class EDB_TemplateAdmin(admin.ModelAdmin):
    list_display = ('operation', 'description')
    ordering = ('operation',)


@admin.register(EDB_Category)
class EDB_CategoryAdmin(admin.ModelAdmin):
    list_display = ('get_templates', 'name', 'order', 'description')
    list_display_links = ('name',)
    ordering = ('order',)

    def get_templates(self, obj):
        return ', '.join([t.description for t in obj.edb_template.all()])
    get_templates.short_description = _('Extend Database Templates')


@admin.register(EDB_Question)
class EDB_QuestionAdmin(admin.ModelAdmin):
    list_display = ('edb_category', 'display_text', 'order', 'type', 'awx_variable_name')
    list_display_links = ('display_text',)
    ordering = ('edb_category', 'order')


@admin.register(SO_Template)
class SO_TemplateAdmin(admin.ModelAdmin):
    list_display = ('operation', 'description')
    ordering = ('operation',)


@admin.register(SO_Category)
class SO_CategoryAdmin(admin.ModelAdmin):
    list_display = ('get_templates', 'name', 'order', 'description')
    list_display_links = ('name',)
    ordering = ('order',)

    def get_templates(self, obj):
        return ', '.join([t.description for t in obj.so_template.all()])
    get_templates.short_description = _('Scale Out Templates')


@admin.register(SO_Question)
class SO_QuestionAdmin(admin.ModelAdmin):
    list_display = ('so_category', 'display_text', 'order', 'awx_variable_name')
    list_display_links = ('display_text',)
    ordering = ('so_category', 'order')


@admin.register(SubscriptionTemplate)
class SubscriptionTemplateAdmin(admin.ModelAdmin):
    form = SubscriptionTemplateForm
    list_display = ('get_services', 'description')

    def get_services(self, obj):
        return ', '.join([str(s) for s in obj.services.all()])
    get_services.short_description = _('Services')


@admin.register(SubscriptionPanel)
class SubscriptionPanelAdmin(admin.ModelAdmin):
    form = SubscriptionPanelForm
    list_display = ('get_templates', 'name', 'fields')
    list_display_links = ('name',)
    ordering = ('name',)

    def get_templates(self, obj):
        return ', '.join([t.description for t in obj.sub_templates.all()])
    get_templates.short_description = _('Subscription Templates')


@admin.register(SubscriptionTab)
class SubscriptionTabAdmin(admin.ModelAdmin):
    list_display = ('get_templates', 'name', 'order', 'fields')
    list_display_links = ('name',)
    ordering = ('order',)

    def get_templates(self, obj):
        return ', '.join([t.description for t in obj.sub_templates.all()])
    get_templates.short_description = _('Subscription Templates')


@admin.register(SubscriptionConfig)
class SubscriptionConfigAdmin(admin.ModelAdmin):
    list_display = ('mapping_value', 'colored_field')

    def colored_field(self, obj):
        return format_html('<span style="color: {}; background-color: {};">{} - {}</span>', obj.text_color, obj.field_color, obj.text_color, obj.field_color)
    colored_field.short_description = _('Font-Background Color')


@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ('configuration', 'server_name', 'is_available')
    list_filter = ('configuration', 'server_name')
    ordering = ('configuration', 'server_name')


@admin.register(LCA_Operator)
class LCA_OperatorAdmin(admin.ModelAdmin):
    list_display = ('field', 'value', 'operator', 'order')


@admin.register(LCA_Config)
class LCA_ConfigAdmin(admin.ModelAdmin):
    form = LCA_ConfigForm
    list_display = ('operation', 'get_operators')
    filter_horizontal = ('operators',)
    ordering = ('operation',)

    def get_operators(self, obj):
        return f"{' '.join([op.field + ':' + op.value + ' ' + str(op.operator) for op in obj.operators.all()])}"
    get_operators.short_description = _('LCA Operators')
