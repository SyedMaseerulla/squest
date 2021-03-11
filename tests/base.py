
from django.contrib.auth.models import User
from django.test import TestCase

from service_catalog.models import TowerServer, JobTemplate, Operation, Service
from service_catalog.models.operations import OperationType


class BaseTest(TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        # ------------------------------
        # USERS
        # ------------------------------
        self.common_password = "p@ssw0rd"
        # staff user (default user for all tests)
        self.superuser = User.objects.create_superuser('admi1234', 'admin@hpe.com', self.common_password)
        self.client.login(username=self.superuser.username, password=self.common_password)
        # standard user
        self.standard_user = User.objects.create_user('stan1234', 'stan.1234@hpe.com', self.common_password)

        # ------------------------------
        # Tower
        # ------------------------------
        self.tower_server_test = TowerServer.objects.create(name="tower-server-test", host="localhost", token="xxx")
        survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "",
                    "max": 1024,
                    "min": 0,
                    "new_question": True,
                    "question_description": "",
                    "question_name": "String variable",
                    "required": True,
                    "type": "text",
                    "variable": "text_variable"
                },
                {
                    "choices": "choice1\nchoice2\nchoice3",
                    "default": "choice1",
                    "max": None,
                    "min": None,
                    "question_description": "",
                    "question_name": "List variable",
                    "required": True,
                    "type": "multiplechoice",
                    "variable": "multiplechoice_variable"
                }

            ]
        }
        self.job_template_test = JobTemplate.objects.create(name="job-template-test",
                                                            survey=survey,
                                                            tower_id=1,
                                                            tower_server=self.tower_server_test)

        self.service_test = Service.objects.create(name="service-test", description="description-of-service-test")

        self.create_operation_test = Operation.objects.create(name="create test",
                                                              service=self.service_test,
                                                              job_template=self.job_template_test)
        self.update_operation_test = Operation.objects.create(name="create test",
                                                              service=self.service_test,
                                                              job_template=self.job_template_test,
                                                              type=OperationType.UPDATE)