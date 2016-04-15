import uuid
import logging

from datetime import datetime


from django.db import models
from django.contrib.auth.models import User

from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

class UploadSession(models.Model):

    """Helper class to keep track of uploads.
    """
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    processed = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)
    context = models.TextField(blank=True, null=True)

    def successful(self):
        return self.processed and self.errors is None