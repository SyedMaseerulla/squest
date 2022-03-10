from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse

#inside mange_surveys
@user_passes_test(lambda u: u.is_superuser)
def manage_surveys(request):
    return redirect(reverse('admin:squest_survey_template_changelist'))
