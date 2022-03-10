# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from service_catalog.models import Operation
from squest_survey.models import Answer, Response, Category, Template, Question, Operation, Calculation, VendorItem, vendor_item


class Command(BaseCommand):
    help = "Populate sample survey"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # clean up existing data
        Answer.objects.all().delete()
        Response.objects.all().delete()
        Operation.objects.all().delete()
        Question.objects.all().delete()
        Calculation.objects.all().delete()
        Category.objects.all().delete()
        Template.objects.all().delete()

        # create categories
        cat_infra = Category.objects.create(name='Infra Configuration', description='Infra Configuration', order=1)
        cat_os = Category.objects.create(name='OS Configuration', description='OS Configuration', order=2, shown=True)
        cat_db = Category.objects.create(name='DB Configuration', description='DB Configuration', order=3, shown=True)
        cat_dp = Category.objects.create(name='Data Protection Configuration', description='Data Protection Configuration', order=4)
        cat_backup = Category.objects.create(name='Bakcup Configuration', description='Bakcup Configuration', order=5, shown=True)

        # create templates
        survey_template = Template.objects.create(name='Demo Template 1', opertaion=Operation.objects.all().last(), type=Template.SURVEY, description='Demo Template 1 DESC', vendor_item=VendorItem.objects.all().first())
        release_ubuntu = Template.objects.create(name='Release', opertaion=None, type=Template.CASCADE, description='For Ubuntu')
        release_windows = Template.objects.create(name='Release', opertaion=None, type=Template.CASCADE, description='For Windows')
        version_12c = Template.objects.create(name='Version', opertaion=None, type=Template.CASCADE, description='For 12c')
        version_18c = Template.objects.create(name='Version', opertaion=None, type=Template.CASCADE, description='For 18c')
        backup_rmen = Template.objects.create(name='Backup', opertaion=None, type=Template.CASCADE, description='For RMEN')
        backup_cohesity = Template.objects.create(name='Backup', opertaion=None, type=Template.CASCADE, description='For Cohesity')
        dp_cdn = Template.objects.create(name='Data Protection', opertaion=None, type=Template.CASCADE, description='For CDN')
        dp_no_cdn = Template.objects.create(name='No Data Protection', opertaion=None, type=Template.CASCADE, description='For No CDN')

        # create infra questions
        qn = Question.objects.create(display_text='Name', order=1, required=True, category=cat_infra, type=Question.INSTANCE_NAME_VALIDATION, choices=None)
        qn.templates.add(survey_template)
        qn = Question.objects.create(display_text='Text', order=2, required=True, category=cat_infra, type=Question.SHORT_TEXT, choices=None)
        qn.templates.add(survey_template)

        # create os questions
        cascade_qn = Question.objects.create(display_text='Release', order=1, required=False, category=cat_os, type=Question.SELECT, choices='Ubuntu,Windows')
        cascade_qn.templates.add(survey_template)
        cascade_qn.cascade_templates.add(release_ubuntu)
        cascade_qn.cascade_templates.add(release_windows)
        qn = Question.objects.create(display_text='Versions', order=2, required=False, category=cat_os, type=Question.SELECT, choices='16.04,18.04,20.04')
        qn.templates.add(release_ubuntu)
        qn = Question.objects.create(display_text='Versions', order=2, required=False, category=cat_os, type=Question.RADIO, choices='7,8,10')
        qn.templates.add(release_windows)
        qn = Question.objects.create(display_text='Dist', order=3, required=False, category=cat_os, type=Question.SELECT, choices='Home,Pro,Ultimate')
        qn.templates.add(release_windows)

        # create db questions
        qn = Question.objects.create(display_text='Password', order=1, required=False, category=cat_db, type=Question.PASSWORD)
        qn.templates.add(survey_template)
        cascade_qn = Question.objects.create(display_text='Release', order=2, required=False, category=cat_db, type=Question.SELECT, choices='12c,18c')
        cascade_qn.templates.add(survey_template)
        cascade_qn.cascade_templates.add(version_12c)
        cascade_qn.cascade_templates.add(version_18c)
        qn = Question.objects.create(display_text='Versions', order=3, required=False, category=cat_db, type=Question.SELECT, choices='12.0.1,12.0.2,12.0.3')
        qn.templates.add(version_12c)
        qn = Question.objects.create(display_text='Versions', order=3, required=False, category=cat_db, type=Question.SELECT, choices='18.0.1,18.0.2,18.0.3')
        qn.templates.add(version_18c)
        # create calculation
        cal_qn1 = Question.objects.create(display_text='Disk Size', order=4, required=False, category=cat_db, type=Question.SELECT, choices='10,20,30')
        cal_qn1.templates.add(survey_template)
        op1 = Operation.objects.create(question=cal_qn1, operator=Operation.TIMES, order=1)
        cal_qn2 = Question.objects.create(display_text='Num of Disk', order=5, required=False, category=cat_db, type=Question.SELECT, choices='5GB,10GB,50GB')
        cal_qn2.templates.add(survey_template)
        op2 = Operation.objects.create(question=cal_qn2, operator=Operation.EQUAL, order=2)
        calculation = Calculation.objects.create(unit='GB')
        calculation.operation.add(op1)
        calculation.operation.add(op2)
        qn = Question.objects.create(display_text='Total DB Size', order=6, required=False, category=cat_db, type=Question.CALCULATED_FIELD, calculation=calculation)
        qn.templates.add(survey_template)

        # create dp questions
        cascade_qn = Question.objects.create(display_text='Backup', order=1, required=False, category=cat_dp, type=Question.SELECT, choices='RMEN,Cohesity')
        cascade_qn.templates.add(survey_template)
        cascade_qn.cascade_templates.add(backup_rmen)
        cascade_qn.cascade_templates.add(backup_cohesity)
        qn = Question.objects.create(display_text='RMEN', order=2, required=False, category=cat_dp, type=Question.INFOMATION_TEXT, info_text='RMEN Information')
        qn.templates.add(backup_rmen)
        qn = Question.objects.create(display_text='Cohesity', order=2, required=False, category=cat_dp, type=Question.INFOMATION_TEXT, info_text='Cohesity Information')
        qn.templates.add(backup_cohesity)

        # create backup questions
        cascade_qn = Question.objects.create(display_text='CDN', order=1, required=False, category=cat_backup, type=Question.RADIO, choices='CDN,No CDN')
        cascade_qn.templates.add(survey_template)
        cascade_qn.cascade_templates.add(dp_cdn)
        cascade_qn.cascade_templates.add(dp_no_cdn)
        qn = Question.objects.create(display_text='Policy', order=2, required=False, category=cat_backup, type=Question.INFOMATION_TEXT, info_text='CDN Policy')
        qn.templates.add(dp_cdn)
