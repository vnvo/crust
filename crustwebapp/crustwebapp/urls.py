from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework_nested import routers

from authentication.views import SupervisorViewSet
from authentication.views import LoginView
from authentication.views import LogoutView

from crustwebapp.views import IndexView

# setup router
router = routers.SimpleRouter()
router.register(r'supervisors', SupervisorViewSet)


urlpatterns = patterns(
    '',
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),

    url('^.*$', IndexView.as_view(), name='index'),
    url(r'^admin/', include(admin.site.urls)),
)
