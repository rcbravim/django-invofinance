
from datetime import datetime

from django.db import models


class User(models.Model):
    use_login = models.EmailField(max_length=250)
    use_password = models.CharField(max_length=128)
    use_is_manager = models.BooleanField(default=False)
    use_is_valid = models.BooleanField(default=False)
    use_status = models.BooleanField(default=False)
    use_date_created = models.DateTimeField(editable=False)
    use_date_updated = models.DateTimeField()
    use_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.use_login

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.use_date_created = datetime.now()
        self.use_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class UserLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True, default=None
    )
    log_user_agent = models.CharField(max_length=250)
    log_ip_address = models.CharField(max_length=250)
    log_ip_type = models.CharField(
        max_length=4, null=True, blank=True, default=None
    )
    log_ip_country = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    log_ip_country_flag = models.CharField(
        max_length=64, null=True, blank=True, default=None
    )
    log_ip_region = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    log_ip_city = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    log_ip_latitude = models.DecimalField(
        max_digits=12, decimal_places=9, null=True, blank=True, default=None
    )
    log_ip_longitude = models.DecimalField(
        max_digits=12, decimal_places=9, null=True, blank=True, default=None
    )
    log_location = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    log_method = models.CharField(
        max_length=16, null=True, blank=True, default=None
    )
    log_risk_level = models.SmallIntegerField(default=0)
    log_risk_comment = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    log_date_created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.log_date_created = datetime.now()
        return super().save(*args, **kwargs)
