# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from django_daraja.models import AccessToken, StkPushResponse

# Register your models here.
admin.site.register(AccessToken)
admin.site.register(StkPushResponse)