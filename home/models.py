
from datetime import datetime

from django.db import models


class User(models.Model):
    use_login = models.EmailField(max_length=250)
    use_password = models.CharField(max_length=128)
    use_status = models.BooleanField(default=False)
    use_date_created = models.DateTimeField(editable=False)
    use_date_updated = models.DateTimeField()
    use_date_deleted = models.DateTimeField(null=True, default=None)

    def __str__(self) -> str:
        return self.use_login

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.use_date_created = datetime.now()
        self.use_date_updated = datetime.now()
        return super().save(*args, **kwargs)
