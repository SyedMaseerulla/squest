# -*- coding: utf-8 -*-

from squest_survey.views.index_view import IndexView, VendorView
from squest_survey.views.survey_detail import SurveyDetail
from squest_survey.views.survey_detail import SurveyRequest
from squest_survey.views.manage_surveys import manage_surveys
from squest_survey.views.extend_database import ExtendDatabase, ExtendDatabaseRequest
from squest_survey.views.scale_out import ScaleOut, ScaleOutRequest
from squest_survey.views.subscription import SubscriptionList, Subscription


MAIN = ['IndexView', 'manage_surveys', 'VendorView']
SURVEY = ['SurveyDetail', 'SurveyRequest']
EDB_SO = ['ExtendDatabase', 'ExtendDatabaseRequest', 'ScaleOut', 'ScaleOutRequest']
SUB = ['SubscriptionList', 'Subscription']

__all__ = MAIN + SURVEY + EDB_SO + SUB
