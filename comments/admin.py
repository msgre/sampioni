# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import AttachmentCategory, Attachment, Comment

admin.site.register(AttachmentCategory)
admin.site.register(Attachment)
admin.site.register(Comment)
