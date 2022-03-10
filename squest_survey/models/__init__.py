# -*- coding: utf-8 -*-

"""
Permit to import everything from squest_survey.models without knowing the details.
"""

from .template import Template
from .category import Category
from .question import Question
from .response import Response
from .answer import Answer
from .calculation import Calculation
from .operation import Operation
from .menu_item import MenuItem
from .vendor_item import VendorItem
from .edb_template import EDB_Template
from .edb_category import EDB_Category
from .edb_question import EDB_Question
from .so_template import SO_Template
from .so_category import SO_Category
from .so_question import SO_Question
from .sub_template import SubscriptionTemplate
from .sub_tab import SubscriptionTab
from .sub_panel import SubscriptionPanel
from .sub_config import SubscriptionConfig
from .lca_operator import LCA_Operator
from .lca_config import LCA_Config
from .hardware import Hardware
from .patch import Patch
from .recovery_tasks import Recovery_tasks


SURVEY = ['Template', 'Category', 'Question', 'Calculation', 'Operation', 'Response', 'Answer']
MENU = ['MenuItem', 'VendorItem']
EDB = ['EDB_Template', 'EDB_Category', 'EDB_Question']
SO = ['SO_Template', 'SO_Category', 'SO_Question']
SUB = ['SubscriptionTemplate', 'SubscriptionTab', 'SubscriptionPanel', 'SubscriptionConfig']
LCA = ['LCA_Operator', 'LCA_Config']
AVAILABLITY = ['Hardware' + 'Patch' + 'Recovery_tasks']

__all__ = SURVEY + MENU + EDB + SO + SUB + LCA + AVAILABLITY
