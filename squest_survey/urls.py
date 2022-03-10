# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from squest_survey.views import IndexView, VendorView, manage_surveys
from squest_survey.views import SurveyDetail, SurveyRequest
from squest_survey.views import ExtendDatabase, ExtendDatabaseRequest
from squest_survey.views import ScaleOut, ScaleOutRequest
from squest_survey.views import SubscriptionList, Subscription


urlpatterns = [
    url(r'^manage_surveys/', manage_surveys, name='manage-surveys'),
    url(r'^extend_database/(?P<instance_id>[0-9]+)-request/', ExtendDatabaseRequest.as_view(), name='extend-database-request'),
    url(r'^extend_database/', ExtendDatabase.as_view(), name='extend-database'),
    url(r'^extend_database/(?P<instance_id>[0-9]+)/', ExtendDatabase.as_view(), name='extend-database'),
    url(r'^scale_out/(?P<instance_id>[0-9]+)-request/', ScaleOutRequest.as_view(), name='scale-out-request'),
    url(r'^scale_out/', ScaleOut.as_view(), name='scale-out'),
    url(r'^scale_out/(?P<instance_id>[0-9]+)/', ScaleOut.as_view(), name='scale-out'),
    url(r'^subscription_list/(?P<vendor_item>[\w-]+)/', SubscriptionList.as_view(), name='subscription-list'),
    url(r'^subscription_list/', SubscriptionList.as_view(), name='subscription-list'),
    url(r'^subscription/(?P<instance_id>[0-9]+)/', Subscription.as_view(), name='subscription'),
    url(r'^(?P<id>[0-9]+)-cascade/', login_required(SurveyDetail.as_view()), name='survey-cascade'),
    url(r'^(?P<id>[0-9]+)-cascade-request/', login_required(SurveyRequest.as_view()), name='survey-cascade-request'),
    url(r'^(?P<request_id>[0-9]+)-(?P<user_id>[0-9]+)-accept/', login_required(SurveyDetail.as_view()), name='survey-accept'),
    url(r'^(?P<request_id>[0-9]+)-(?P<user_id>[0-9]+)-accept-request/', login_required(SurveyRequest.as_view()), name='survey-accept-request'),
    url(r'^(?P<operation_id>[0-9]+)-(?P<instance_id>[0-9]+)-operation/', login_required(SurveyDetail.as_view()), name='survey-operation'),
    url(r'^(?P<operation_id>[0-9]+)-(?P<instance_id>[0-9]+)-operation-request/', login_required(SurveyRequest.as_view()), name='survey-operation-request'),
    url(r'^(?P<menu_item>[\w-]+)/(?P<vendor_item>[\w-]+)/', VendorView.as_view(), name='survey-vendor-list'),
    url(r'^(?P<menu_item>[\w-]+)/', IndexView.as_view(), name='survey-list'),
]
