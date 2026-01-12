from django.contrib import admin
from .models import AdminProfile, Branch, Forms, FormAttachment

admin.site.register(AdminProfile)
admin.site.register(Branch)
admin.site.register(Forms)
admin.site.register(FormAttachment)
