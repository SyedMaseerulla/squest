from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user
from service_catalog.filters.request_filter import RequestFilter
from service_catalog.models import Request
from service_catalog.tables.request_tables import RequestTable


class RequestListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = RequestTable
    model = Request
    template_name = 'generics/request_list.html'
    ordering = '-date_submitted'

    filterset_class = RequestFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        if self.request.user.is_superuser:
            return Request.objects.all().distinct() & filtered
        else:
            return get_objects_for_user(self.request.user, 'service_catalog.view_request').distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Requests"
        context['html_button_path'] = "generics/buttons/request-archived-list.html"
        if self.request.user.is_superuser:
            requests = Request.objects.all().distinct()
        else:
            requests = get_objects_for_user(self.request.user, 'service_catalog.view_request').distinct()
        context['requests'] = requests
        return context
