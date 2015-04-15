from django.conf.urls import patterns, include, url
from django.contrib import admin

from crustwebapp.views import IndexView

urlpatterns = patterns('',
    url('^.*$', IndexView.as_view(), name='index'),
    url(r'^admin/', include(admin.site.urls)),
)
