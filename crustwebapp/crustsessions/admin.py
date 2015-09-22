from django.contrib import admin
from crustsessions.models import CrustCLISession, CrustSessionEvent


class CrustSessionEventInLine(admin.StackedInline):
    model = CrustSessionEvent

class CrustCLISessionInline(admin.ModelAdmin):
    inlines = [CrustSessionEventInLine]

admin.site.register(CrustCLISession, CrustCLISessionInline)
