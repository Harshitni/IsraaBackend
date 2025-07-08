from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import NotRegistered

try:
    admin.site.unregister(LogEntry)
except NotRegistered:
    pass  # It's okay if LogEntry is not registered
