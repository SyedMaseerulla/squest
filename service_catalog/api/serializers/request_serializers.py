from guardian.shortcuts import get_objects_for_user
from rest_framework.generics import get_object_or_404
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, CharField, ValidationError

from profiles.api.serializers.user_serializers import UserSerializer
from profiles.models import BillingGroup
from service_catalog.forms import FormUtils
from service_catalog.models import Request, Service, OperationType, Operation, Instance, RequestMessage
from service_catalog.api.serializers import DynamicSurveySerializer, InstanceReadSerializer


class ServiceRequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = ['instance_name', 'billing_group', 'request_comment', 'fill_in_survey']

    instance_name = CharField(
        label="Squest instance name",
        help_text="Help to identify the requested service in the 'Instances' view"
    )
    request_comment = CharField(
        label="Comment",
        help_text="Add a comment to your request",
        required=False
    )
    billing_group = PrimaryKeyRelatedField(label='billing group id', allow_null=True, default=None, required=False,
                                           queryset=BillingGroup.objects.all(),
                                           help_text="Billing group id")

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', None)
        self.view = context.get('view', None)
        self.service_id = self.view.kwargs.get('pk', None)
        self.request = context.get('request', None)
        super(ServiceRequestSerializer, self).__init__(*args, **kwargs)
        if self.service_id is not None:
            self.service = get_object_or_404(Service.objects.filter(enabled=True), id=self.service_id)
            # get the create operation of this service
            self.create_operation = Operation.objects.get(service=self.service, type=OperationType.CREATE)
            # get all field that are not disabled by the admin
            purged_survey = FormUtils.get_available_fields(
                job_template_survey=self.create_operation.job_template.survey,
                operation_survey=self.create_operation.tower_survey_fields)
            self.fields['fill_in_survey'] = DynamicSurveySerializer(fill_in_survey=purged_survey)

    def validate_billing_group(self, value):
        if not self.service.billing_group_is_selectable:
            return None if self.service.billing_group_id is None else BillingGroup.objects.get(
                id=self.service.billing_group_id)
        if value is not None:
            if self.service.billing_groups_are_restricted and value not in self.request.user.billing_groups.all():
                raise ValidationError(
                    f"You are not authorized to request this service with the billing group {value.name}. "
                    f"Please choose among yours"
                )
        return value

    def save(self):
        # create the instance
        instance_name = self.validated_data["instance_name"]
        billing_group = None
        if self.validated_data["billing_group"]:
            billing_group = self.validated_data["billing_group"]

        new_instance = Instance.objects.create(service=self.service, name=instance_name, billing_group=billing_group,
                                               spoc=self.request.user)
        # create the request
        new_request = Request.objects.create(instance=new_instance,
                                             operation=self.create_operation,
                                             fill_in_survey=self.validated_data["fill_in_survey"],
                                             user=self.request.user)

        # save the comment
        message = None
        if "request_comment" in self.validated_data and self.validated_data["request_comment"] is not None:
            comment = self.validated_data["request_comment"]
            message = RequestMessage.objects.create(request=new_request, sender=self.request.user, content=comment)
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=new_request.user, message=message)
        return new_request


class OperationRequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = ['request_comment', 'fill_in_survey']

    request_comment = CharField(
        label="Comment",
        help_text="Add a comment to your request",
        required=False
    )

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', None)
        self.view = context.get('view', None)
        self.request = context.get('request', None)
        operation_id = self.view.kwargs.get('operation_id', None)
        instance_id = self.view.kwargs.get('instance_id', None)
        super(OperationRequestSerializer, self).__init__(*args, **kwargs)
        if operation_id is not None and instance_id is not None:
            self.target_operation = get_object_or_404(Operation.objects.exclude(type=OperationType.CREATE),
                                                      id=operation_id)
            self.target_instance = get_object_or_404(
                get_objects_for_user(self.request.user, 'service_catalog.view_instance'), id=instance_id)

            # get all field that are not disabled by the admin
            purged_survey = FormUtils.get_available_fields(
                job_template_survey=self.target_operation.job_template.survey,
                operation_survey=self.target_operation.tower_survey_fields)
            self.fields['fill_in_survey'] = DynamicSurveySerializer(fill_in_survey=purged_survey)

    def save(self, **kwargs):
        new_request = Request.objects.create(instance=self.target_instance,
                                             operation=self.target_operation,
                                             fill_in_survey=self.validated_data["fill_in_survey"],
                                             user=self.request.user)
        # save the comment
        message = None
        if "request_comment" in self.validated_data and self.validated_data["request_comment"] is not None:
            comment = self.validated_data["request_comment"]
            message = RequestMessage.objects.create(request=new_request, sender=self.request.user, content=comment)
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=new_request.user, message=message)
        return new_request


class RequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        exclude = ['periodic_task', 'periodic_task_date_expire', 'failure_message', 'admin_fill_in_survey']
        read_only = True

    instance = InstanceReadSerializer(read_only=True)
    user = UserSerializer(read_only=True)


class AdminRequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        exclude = ['periodic_task', 'periodic_task_date_expire', 'failure_message']

    instance = InstanceReadSerializer(read_only=True)
    user = UserSerializer(read_only=True)
