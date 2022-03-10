from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Recovery_tasks(models.Model):
    backup_type = models.CharField(_('Backup Type'),max_length=63)
    completion_time = models.CharField(_('Completion Time'),max_length=25)
    db_name = models.CharField(_('DB Name'),max_length=100)
    recover_task = models.CharField(_('Recover Task'),max_length=200)
    subscription_name = models.CharField(_('Subscription Name'),max_length=63)
    tag = models.CharField(_('TAG'),max_length=200)
    db_server_ip = models.CharField(_('DBServerIp'),max_length=20)
    ora_db_version = models.CharField(_('DBServerIp'),max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Recovery Task')
        verbose_name_plural = _('Recovery Tasks')