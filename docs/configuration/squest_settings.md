# Configuration  settings

Default settings are configured to provide a testing/development environment. For a production setup it is recommended
to adjust them following you production target environment.

The configuration is loaded from environment variables file placed in the folder `docker/environment_variables`.

## Database

### MYSQL_DATABASE

**Default:** `squest_db`

Mysql database name.

### MYSQL_USER

**Default:** `squest_user`

Mysql user used to connect to the `MYSQL_DATABASE` name.

### MYSQL_PASSWORD

**Default:** `squest_password`

Password of the `MYSQL_USER` username.  

### MYSQL_HOST

**Default:** `127.0.0.1`

Mysql database host. The default value is localhost to match the development configuration. 
Switch to `db` in production when using the docker-compose based deployment.

### MYSQL_PORT

**Default:** `3306`

Mysql database port.

## Authentication

### LDAP_ENABLED

**Default:** `False`

Set to `True` to enable LDAP based authentication. [See configuration doc](../installation/ldap.md).  

## Squest

### SQUEST_HOST

**Default:** `http://squest.domain.local`

Address of the Squest portal instance. Used in email templates and in metadata sent to Tower job templates.

### SQUEST_EMAIL_HOST

**Default:** `squest.domain.local`

Domain name used as email sender. E.g: "squest@squest.domain.local". 

### SQUEST_EMAIL_NOTIFICATION_ENABLED

**Default:** Based on `DEBUG` value by default

Set to `True` to enable email notifications.  

## SMTP

### EMAIL_HOST

**Default:** `localhost`

The SMTP host to use for sending email.

### EMAIL_PORT

**Default:** `25`

Port to use for the SMTP server defined in `EMAIL_HOST`.  

## Backup

### BACKUP_ENABLED

**Default:** `False`

Switch to `True` to enable backup. Refer to the [dedicated documentation](../installation/backup.md).

### BACKUP_CRONTAB

**Default:** `0 1 * * *`

Crontab line for backup. By default, the backup is performed every day at 1AM.

### DBBACKUP_CLEANUP_KEEP

**Default:** `5`

Number of db backup file to keep. [Doc](https://django-dbbackup.readthedocs.io/en/master/configuration.html#dbbackup-cleanup-keep-and-dbbackup-cleanup-keep-media).

### DBBACKUP_CLEANUP_KEEP_MEDIA

**Default:** `5`

Number of media backup tar to keep. [Doc](https://django-dbbackup.readthedocs.io/en/master/configuration.html#dbbackup-cleanup-keep-and-dbbackup-cleanup-keep-media).

## Metrics

### METRICS_ENABLED

**Default:** `False`

Switch to `True` to enable Prometheus metrics page.

### METRICS_PASSWORD_PROTECTED

**Default:** `True`

Switch to `False` to disable the basic authentication on metrics page.

### METRICS_AUTHORIZATION_USERNAME

**Default:** `admin`

Username for the basic authentication of the metrics page.

### METRICS_AUTHORIZATION_PASSWORD

**Default:** `admin`

Password for the basic authentication of the metrics page.

## Auto cleanup

### DOC_IMAGES_CLEANUP_ENABLED

**Default:** `False`

Switch to `True` to enable automatic cleanup of ghost docs images from media folder.

### DOC_IMAGES_CLEANUP_CRONTAB

**Default:** `30 1 * * *`

Crontab line for ghost image cleanup. By default performed every day at 1:30 AM.

## Production

### SECRET_KEY

**Default:**  Default randomly-generated

Django secret key used for cryptographic signing. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-SECRET_KEY).

### DEBUG

**Default:** True

Django DEBUG mode. Switch to `False` for production.

### ALLOWED_HOSTS

**Default:** `*`

Comma separated list of allowed FQDN. Refer to the complete [documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts).   

### CELERY_BROKER_URL

**Default:** `amqp://rabbitmq:rabbitmq@localhost:5672/squest`

RabbitMQ message broker URL. The default value is localhost to match the development configuration. 
Replace `localhost` by `rabbitmq` in production when using the docker-compose based deployment.

### CELERY_TASK_SOFT_TIME_LIMIT

**Default:** `300`

Async task execution timeout. [Doc](https://docs.celeryproject.org/en/v2.2.4/configuration.html#celeryd-task-soft-time-limit).

### LANGUAGE_CODE

**Default:** `en-us`

Django language. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#language-code)

### TIME_ZONE

**Default:** `Europe/Paris`

Time zone of the server that host Squest service. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-TIME_ZONE)
