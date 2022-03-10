# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from squest_survey.models import EDB_Category, EDB_Question


class Command(BaseCommand):
    help = "Populate initial extend questions"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        EDB_Question.objects.all().delete()
        EDB_Category.objects.all().delete()

        cat_extend = EDB_Category.objects.create(name='Extend Configuration', description='Extend Configuration', order=9, extended=True)
        EDB_Question.objects.create(display_text='Lun Size', edb_category=cat_extend, order=1, type=EDB_Question.EDB_LUN_SIZE)
        EDB_Question.objects.create(display_text='Num of Lun', edb_category=cat_extend, order=2, type=EDB_Question.SELECT, choices='5,10,50')
        EDB_Question.objects.create(display_text='Total Lun Size', edb_category=cat_extend, order=3, type=EDB_Question.CALCULATED_FIELD)
