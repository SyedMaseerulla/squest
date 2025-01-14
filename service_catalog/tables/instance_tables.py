from django_tables2 import TemplateColumn, LinkColumn
from django_tables2.utils import A

from service_catalog.models import Instance
from Squest.utils.squest_table import SquestTable


class InstanceTable(SquestTable):
    state = TemplateColumn(template_name='custom_columns/instance_state.html')
    service__name = TemplateColumn(template_name='custom_columns/instance_type.html', verbose_name="Type")
    opened_support_count = TemplateColumn(template_name='custom_columns/instance_opened_support.html',
                                          verbose_name="Opened support")
    name = LinkColumn("service_catalog:instance_details", args=[A("id")], verbose_name="Name")

    class Meta:
        model = Instance
        attrs = {"id": "instance_table", "class": "table squest-pagination-tables"}
        fields = ("name", "service__name", "state", "opened_support_count", "spoc", "date_available")
