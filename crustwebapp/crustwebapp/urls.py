from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework_nested import routers

from authentication.views import SupervisorViewSet
from authentication.views import LoginView
from authentication.views import LogoutView

from servers.views import ServerGroupsViewSet, ServerGroupsCountView
from servers.views import ServersViewSet, ServersCountView
from servers.views import ServerAccountsViewSet, ServerAccountsCountView

from remoteusers.views import RemoteUsersViewSet
from remoteusers.views import RemoteUsersCountView

from commandgroups.views import CommandGroupsViewSet
from commandgroups.views import CommandGroupsCountView
from commandgroups.views import CommandPatternsViewSet
from commandgroups.views import CommandPatternsCountView

from remoteuseracl.views import RemoteUserACLViewSet
from remoteuseracl.views import RemoteUserACLCountView

from supervisoracl.views import SupervisorACLViewSet
from supervisoracl.views import SupervisorACLCountView

from crustwebapp.views import IndexView

# setup router
router = routers.SimpleRouter()
router.register(r'supervisors', SupervisorViewSet, base_name='supervisor')
router.register(r'servergroups', ServerGroupsViewSet, base_name='servergroup')
router.register(r'servers', ServersViewSet, base_name='server')
router.register(r'serveraccounts', ServerAccountsViewSet, base_name='serveraccount')
router.register(r'remoteusers', RemoteUsersViewSet, base_name='remoteuser')
router.register(r'commandgroups', CommandGroupsViewSet, base_name='commandgroup')
router.register(r'commandpatterns', CommandPatternsViewSet)
router.register(r'remoteuseracls', RemoteUserACLViewSet)
router.register(r'supervisoracls', SupervisorACLViewSet)

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    ### Dashboard General Stats
    url(r'^api/v1/servergroups/count/$',
        ServerGroupsCountView.as_view(),
        name='servergroups-count'),

    url(r'api/v1/servers/count/$',
        ServersCountView.as_view(),
        name='servers-count'),

    url(r'api/v1/serveraccounts/count/$',
        ServerAccountsCountView.as_view(),
        name='serveraccount-count'),

    url(r'api/v1/remoteusers/count/$',
        RemoteUsersCountView.as_view(),
        name='remoteusers-count'),

    url(r'api/v1/commandgroups/count/$',
        CommandGroupsCountView.as_view(),
        name='commandgroups-count'),

    url(r'api/v1/commandpatterns/count/$',
        CommandPatternsCountView.as_view(),
        name='commandpattern-count'),

    url(r'api/v1/remoteuseracls/count/$',
        RemoteUserACLCountView.as_view(),
        name='remoteuseracl-count'),

    url(r'api/v1/supervisoracls/count/$',
        SupervisorACLCountView.as_view(),
        name='supervisoracl-count'),

    ### Model View Routes
    url(r'^api/v1/', include(router.urls)),


    ### Authentication
    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),

    url('^.*$', IndexView.as_view(), name='index'),
    #url(r'^admin/', include(admin.site.urls)),
)
