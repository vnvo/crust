from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework_nested import routers

from authentication.views import SupervisorViewSet
from authentication.views import LoginView
from authentication.views import LogoutView

from servers.views import ServerGroupsViewSet
from servers.views import ServerGroupsCountView
from servers.views import ServersViewSet
from servers.views import ServersCountView

from crustwebapp.views import IndexView

# setup router
router = routers.SimpleRouter()
router.register(r'supervisors', SupervisorViewSet)
router.register(r'servergroups', ServerGroupsViewSet)
router.register(r'servers', ServersViewSet)

urlpatterns = patterns(
    '',

    ### Dashboard General Stats
    url(r'^api/v1/servergroups/count/$',
        ServerGroupsCountView.as_view(),
        name='servergroups-count'),

    url(r'api/v1/servers/count/$',
        ServersCountView.as_view(),
        name='servers-count'),


    ### Model View Routes
    url(r'^api/v1/', include(router.urls)),

    ### Authentication
    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),

    url('^.*$', IndexView.as_view(), name='index'),
    url(r'^admin/', include(admin.site.urls)),
)
