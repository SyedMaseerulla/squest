from django.urls import reverse

from service_catalog.models import Operation, Service, OperationType
from tests.test_service_catalog.base import BaseTest


class ServiceDeleteTestCase(BaseTest):

    def setUp(self):
        super(ServiceDeleteTestCase, self).setUp()
        args = {
            "service_id": self.service_test.id
        }
        self.url = reverse('service_catalog:edit_service', kwargs=args)
        self.data = {
            "name": "service-test-updated",
            "description": "description-of-service-test-updated",
            "billing": "defined",
            "billing_group_id": "",
            "billing_group_is_shown": "on",
            "enabled": False
        }

    def test_admin_can_edit_service(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(302, response.status_code)
        self.service_test.refresh_from_db()
        self.assertEqual(self.service_test.name, "service-test-updated")
        self.assertEqual(self.service_test.description, "description-of-service-test-updated")

    def test_standard_user_cannot_edit_service(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(302, response.status_code)
        self.service_test.refresh_from_db()
        self.assertEqual(self.service_test.name, "service-test")
        self.assertEqual(self.service_test.description, "description-of-service-test")

    def test_hide_service_after_disabled(self):
        service_count = Service.objects.all().count()
        response = self.client.get(reverse("service_catalog:service_list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["services"].count(), service_count)
        self.client.post(self.url, data=self.data)
        self.service_test.refresh_from_db()
        self.assertFalse(self.service_test.enabled)
        response = self.client.get(reverse("service_catalog:service_list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["services"].count(), service_count - 1)
        response = self.client.get(reverse("service_catalog:customer_service_request",
                                           kwargs={'service_id': self.service_test.id}))
        self.assertEqual(404, response.status_code)
