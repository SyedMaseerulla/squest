# Generated by Django 3.1.14 on 2022-03-10 07:11

import colorfield.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service_catalog', '0005_auto_20220310_0811'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Calculation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(blank=True, max_length=15, null=True, verbose_name='Unit')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('order', models.IntegerField(verbose_name='Display order')),
                ('description', models.CharField(blank=True, max_length=1023, null=True, verbose_name='Description')),
                ('shown', models.BooleanField(default=False, verbose_name='Show DESC?')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='EDB_Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127, verbose_name='Name')),
                ('order', models.IntegerField(blank=True, null=True, verbose_name='Display Order')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('extended', models.BooleanField(default=False, verbose_name='Is Extended Category?')),
            ],
            options={
                'verbose_name': 'EDB Category',
                'verbose_name_plural': 'EDB Categories',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='LCA_Operator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=31, verbose_name='Field')),
                ('value', models.CharField(max_length=31, verbose_name='Value')),
                ('operator', models.CharField(choices=[('&', '&'), ('|', '|'), ('>', '>'), ('<', '<'), ('ON', 'ON'), ('OFF', 'OFF')], max_length=15, verbose_name='Operator')),
                ('order', models.PositiveIntegerField(verbose_name='Order')),
            ],
            options={
                'verbose_name': 'LCA Operator',
                'verbose_name_plural': 'LCA Operators',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True, verbose_name='Name')),
                ('order', models.IntegerField(verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Menu Item',
                'verbose_name_plural': 'Menu Items',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Patch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=63)),
                ('patch_file', models.CharField(max_length=200)),
                ('patch_type', models.CharField(max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'patch',
                'verbose_name_plural': 'patches',
            },
        ),
        migrations.CreateModel(
            name='Recovery_tasks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('backup_type', models.CharField(max_length=63, verbose_name='Backup Type')),
                ('completion_time', models.CharField(max_length=25, verbose_name='Completion Time')),
                ('db_name', models.CharField(max_length=100, verbose_name='DB Name')),
                ('recover_task', models.CharField(max_length=200, verbose_name='Recover Task')),
                ('subscription_name', models.CharField(max_length=63, verbose_name='Subscription Name')),
                ('tag', models.CharField(max_length=200, verbose_name='TAG')),
                ('db_server_ip', models.CharField(max_length=20, verbose_name='DBServerIp')),
                ('ora_db_version', models.CharField(max_length=20, verbose_name='DBServerIp')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Recovery Task',
                'verbose_name_plural': 'Recovery Tasks',
            },
        ),
        migrations.CreateModel(
            name='SO_Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127, verbose_name='Name')),
                ('order', models.IntegerField(blank=True, null=True, verbose_name='Display Order')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'SO Category',
                'verbose_name_plural': 'SO Categories',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='SubscriptionConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mapping_value', models.CharField(max_length=31, unique=True, verbose_name='Mapping Value')),
                ('text_color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=None)),
                ('field_color', colorfield.fields.ColorField(default='#000000', image_field=None, max_length=18, samples=None)),
            ],
            options={
                'verbose_name': 'Subscription Config',
                'verbose_name_plural': 'Subscription Configs',
            },
        ),
        migrations.CreateModel(
            name='VendorItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, unique=True, verbose_name='Name')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images', verbose_name='Image')),
                ('order', models.IntegerField(verbose_name='Order')),
                ('show_edb', models.BooleanField(default=True, verbose_name='Show EDB?')),
                ('edb_image', models.ImageField(blank=True, null=True, upload_to='images', verbose_name='EDB Image')),
                ('show_so', models.BooleanField(default=True, verbose_name='Show SO?')),
                ('so_image', models.ImageField(blank=True, null=True, upload_to='images', verbose_name='SO Image')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vendors', to='squest_survey.menuitem', verbose_name='Menu Item')),
                ('services', models.ManyToManyField(related_name='vendors', to='service_catalog.Service', verbose_name='Service')),
            ],
            options={
                'verbose_name': 'Vendor Item',
                'verbose_name_plural': 'Vendor Items',
                'ordering': ('menu_item', 'order'),
                'unique_together': {('menu_item', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('type', models.CharField(choices=[('survey', 'Survey'), ('cascade', 'Cascade'), ('LCA', 'LCA')], default='survey', max_length=31, verbose_name='Type')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images', verbose_name='Image')),
                ('operation', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='template', to='service_catalog.operation', verbose_name='Operation')),
                ('vendor_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='squest_survey.vendoritem', verbose_name='Vendor Item')),
            ],
            options={
                'verbose_name': 'template',
                'verbose_name_plural': 'templates',
                'ordering': ('type', 'operation'),
            },
        ),
        migrations.CreateModel(
            name='SubscriptionTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Description')),
                ('services', models.ManyToManyField(related_name='sub_templates', to='service_catalog.Service', verbose_name='Service')),
            ],
            options={
                'verbose_name': 'Subscription Template',
                'verbose_name_plural': 'Subscription Templates',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionTab',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, verbose_name='Name')),
                ('fields', models.TextField(help_text='Provide a comma-separated list of AWX variable names\n    for subscription page, ordering with respect to this list.', verbose_name='Fields')),
                ('titles', models.TextField(help_text='Provide a comma-separated list of titles for fields\n    for subscription page, ordering with respect to field list.', verbose_name='Titles')),
                ('order', models.IntegerField(verbose_name='Display Order')),
                ('sub_templates', models.ManyToManyField(related_name='tabs', to='squest_survey.SubscriptionTemplate', verbose_name='Subscription Template')),
            ],
            options={
                'verbose_name': 'Subscription Tab',
                'verbose_name_plural': 'Subscription Tabs',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPanel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, verbose_name='Name')),
                ('fields', models.TextField(help_text='Provide a comma-separated list of AWX variable names\n    for subscription page, ordering with respect to this list.', verbose_name='Fields')),
                ('titles', models.TextField(help_text='Provide a comma-separated list of titles for fields\n    for subscription page, ordering with respect to field list.', verbose_name='Titles')),
                ('sub_templates', models.ManyToManyField(related_name='panels', to='squest_survey.SubscriptionTemplate', verbose_name='Subscription Panel')),
            ],
            options={
                'verbose_name': 'Subscription Panel',
                'verbose_name_plural': 'Subscription Panels',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SO_Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Description')),
                ('operation', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='service_catalog.operation', verbose_name='Operation')),
            ],
            options={
                'verbose_name': 'SO Template',
                'verbose_name_plural': 'SO Templates',
                'ordering': ('operation',),
            },
        ),
        migrations.CreateModel(
            name='SO_Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_text', models.CharField(max_length=127, verbose_name='Display Text')),
                ('awx_variable_name', models.CharField(default='awx', max_length=31, verbose_name='AWX Variable Name')),
                ('order', models.IntegerField(verbose_name='Display Order')),
                ('type', models.CharField(choices=[('hardware-availablity', 'hardware availablity'), ('readonly-text', 'readonly text')], default='readonly-text', max_length=31, verbose_name='Type')),
                ('so_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='questions', to='squest_survey.so_category', verbose_name='Scale Out Category')),
            ],
            options={
                'verbose_name': 'SO Question',
                'verbose_name_plural': 'SO Questions',
                'ordering': ('so_category', 'order'),
            },
        ),
        migrations.AddField(
            model_name='so_category',
            name='so_template',
            field=models.ManyToManyField(related_name='categorys', to='squest_survey.SO_Template', verbose_name='Scale Out Template'),
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('uuid', models.CharField(max_length=36, verbose_name='Feedback unique identifier')),
                ('type', models.CharField(choices=[('survey', 'survey'), ('admin-accept', 'admin accept'), ('new-operation', 'new operation')], default='survey', max_length=31, verbose_name='Type')),
                ('request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='service_catalog.request', verbose_name='Request')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='responses', to='squest_survey.template', verbose_name='Template')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Response',
                'verbose_name_plural': 'Responses',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_text', models.CharField(max_length=127, verbose_name='Display Text')),
                ('awx_variable_name', models.CharField(default='awx', max_length=127, verbose_name='AWX Variable Name')),
                ('is_var_not_required', models.BooleanField(default=False, verbose_name='Don not send this as extra var to awx')),
                ('order', models.IntegerField(verbose_name='Order')),
                ('required', models.BooleanField(verbose_name='Required')),
                ('type', models.CharField(choices=[('short-text', 'short text (one line)'), ('text', 'text (multiple line)'), ('radio', 'radio'), ('select', 'select'), ('integer', 'integer'), ('password', 'password'), ('infomation-text', 'text (infomation)'), ('instance-name-validation', 'instance name validation'), ('calculated-field', 'calculated field'), ('regex-validation', 'regex validation'), ('readonly-text', 'readonly text'), ('hidden-field', 'hidden field'), ('hardware-availablity', 'hardware availablity'), ('hardware-nodes-availablity', 'hardware nodes availablity'), ('hardware-nodes-rac-availablity', 'hardware nodes rac availablity'), ('patch-type-availablity', 'patch type availablity'), ('patch_names', 'patch names'), ('recovery-tasks', 'recovery tasks'), ('recovery-object', 'recovery object'), ('recovery-point', 'recovery point'), ('deprovision-rac-select', 'deprovision rac select'), ('deprovision-rac-nodes', 'deprovision rac nodes')], default='short-text', max_length=31, verbose_name='Type')),
                ('choices', models.TextField(blank=True, help_text="The choices field is only used if the question type     is 'radio', 'select', or 'select multiple' provide a     comma-separated list of options for this question.", null=True, verbose_name='Choices')),
                ('numeric_response', models.BooleanField(default=False, verbose_name='Is Numeric Response?')),
                ('boolean_response', models.BooleanField(default=False, verbose_name='Is Boolean Response?')),
                ('info_text', models.TextField(blank=True, help_text="This field is only used if the question type is     'infomation-text', provide a read only text information.", null=True, verbose_name='Info Text')),
                ('regex_text', models.CharField(blank=True, help_text="This field is only used if the question type is     'regex-field', provide a regex validation.", max_length=255, null=True, verbose_name='Regular Expression')),
                ('readonly_text', models.CharField(blank=True, max_length=127, null=True, verbose_name='Readonly Text Input')),
                ('calculation', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='squest_survey.calculation', verbose_name='Calculations')),
                ('cascade_templates', models.ManyToManyField(blank=True, related_name='cascade_questions', to='squest_survey.Template', verbose_name='Cascade Templates')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='questions', to='squest_survey.category', verbose_name='Category')),
                ('templates', models.ManyToManyField(related_name='questions', to='squest_survey.Template', verbose_name='Templates')),
            ],
            options={
                'verbose_name': 'question',
                'verbose_name_plural': 'questions',
                'ordering': ('category', 'order'),
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator', models.CharField(choices=[('+', 'addition'), ('-', 'subtraction'), ('×', 'multiplication'), ('÷', 'division'), ('=', 'equation')], max_length=15, verbose_name='Operator')),
                ('order', models.PositiveIntegerField(verbose_name='Order')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='operations', to='squest_survey.question', verbose_name='Question')),
            ],
            options={
                'verbose_name': 'operation',
                'verbose_name_plural': 'operations',
                'ordering': ('question__templates', 'order'),
            },
        ),
        migrations.CreateModel(
            name='LCA_Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='service_catalog.operation', verbose_name='Operation')),
                ('operators', models.ManyToManyField(to='squest_survey.LCA_Operator', verbose_name='Operators')),
            ],
            options={
                'verbose_name': 'LCA Config',
                'verbose_name_plural': 'LCA Configs',
            },
        ),
        migrations.CreateModel(
            name='Hardware',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('configuration', models.CharField(max_length=63, verbose_name='Configuration')),
                ('server_name', models.CharField(max_length=127, verbose_name='Server Name')),
                ('availability', models.BooleanField(default=False, verbose_name='Is Available?')),
                ('oneview_hostname', models.CharField(max_length=127)),
                ('remarks', models.CharField(blank=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Hardware',
                'verbose_name_plural': 'Hardwares',
                'ordering': ('configuration', 'server_name'),
                'unique_together': {('configuration', 'server_name', 'availability')},
            },
        ),
        migrations.CreateModel(
            name='EDB_Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Description')),
                ('operation', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='service_catalog.operation', verbose_name='Operation')),
            ],
            options={
                'verbose_name': 'EDB Template',
                'verbose_name_plural': 'EDB Templates',
                'ordering': ('operation',),
            },
        ),
        migrations.CreateModel(
            name='EDB_Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_text', models.CharField(max_length=127, verbose_name='Display Text')),
                ('awx_variable_name', models.CharField(default='awx', max_length=31, verbose_name='AWX Variable Name')),
                ('boolean_response', models.BooleanField(default=False, verbose_name='Is Boolean Response?')),
                ('numeric_response', models.BooleanField(default=False, verbose_name='Is Numeric Response?')),
                ('order', models.IntegerField(verbose_name='Display Order')),
                ('type', models.CharField(choices=[('radio', 'radio'), ('select', 'select'), ('infomation-text', 'text (infomation)'), ('calculated-field', 'calculated field'), ('edb-lun-size', 'edb lun size')], default='infomation-text', max_length=31, verbose_name='Type')),
                ('choices', models.TextField(blank=True, null=True, verbose_name='Choices')),
                ('edb_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='questions', to='squest_survey.edb_category', verbose_name='EDB_Category')),
            ],
            options={
                'verbose_name': 'EDB Question',
                'verbose_name_plural': 'EDB Questions',
                'ordering': ('edb_category', 'order'),
            },
        ),
        migrations.AddField(
            model_name='edb_category',
            name='edb_template',
            field=models.ManyToManyField(related_name='categorys', to='squest_survey.EDB_Template', verbose_name='EDB_Template'),
        ),
        migrations.AddField(
            model_name='calculation',
            name='operation',
            field=models.ManyToManyField(to='squest_survey.Operation', verbose_name='Operation'),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Content')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='squest_survey.question', verbose_name='Question')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='squest_survey.response', verbose_name='Response')),
            ],
            options={
                'verbose_name': 'answer',
                'verbose_name_plural': 'answers',
                'ordering': ('response', 'question'),
            },
        ),
    ]
