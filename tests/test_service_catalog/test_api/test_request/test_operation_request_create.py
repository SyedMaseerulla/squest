from collections import OrderedDict

from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Request
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiOperationRequestCreate(BaseTestRequest):

    def setUp(self):
        super(TestApiOperationRequestCreate, self).setUp()
        self.kwargs = {
            "instance_id": self.test_instance.id,
            "operation_id": self.update_operation_test.id,
        }
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        self.data = {
            'fill_in_survey': {
                'text_variable': 'my text'
            }
        }
        self.expected = {
            'fill_in_survey': OrderedDict([
                ('text_variable', 'my text')
            ])}

    def test_can_create(self):
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(request_count + 1, Request.objects.count())
        self.assertEqual(response.data, self.expected)

    def test_cannot_create_on_provisioning_operation(self):
        self.kwargs = {
            "instance_id": self.test_instance.id,
            "operation_id": self.create_operation_test.id,
        }
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request_count, Request.objects.count())

    def test_cannot_create_on_non_own_instance(self):
        self.client.force_login(self.standard_user_2)
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request_count, Request.objects.count())

    def test_cannot_create_when_logout(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_on_non_existing_instance(self):
        self.kwargs['instance_id'] = 9999999
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_create_on_non_existing_operation(self):
        self.kwargs['operation_id'] = 9999999
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_create_with_wrong_survey_fields(self):
        self.data['fill_in_survey']['wrong_field_name'] = self.data['fill_in_survey'].pop('text_variable')
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_create_with_comment(self):
        self.client.force_login(user=self.standard_user)
        self.data = {
            'fill_in_survey': {
                'text_variable': 'my text'
            },
            "request_comment": "here_is_a_comment"
        }
        self.expected = {
            'fill_in_survey': {
                'text_variable': 'my text'
            },
            "request_comment": "here_is_a_comment"
        }

        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(request_count + 1, Request.objects.count())
        created_request = Request.objects.latest('id')
        self.assertEqual(created_request.comments.count(), 1)
        self.assertEqual(created_request.comments.first().content, "here_is_a_comment")
        self.assertEqual(created_request.comments.first().sender, self.standard_user)
