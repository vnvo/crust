(function (){
    'use strict';

    angular
        .module('crust.crustsessions.services')
        .factory('CrustSessions', CrustSessions);

    CrustSessions.$inject = ['$http'];

    function CrustSessions($http){
        var CrustSessions = {
            all: getAllSessions,
            allActive: getAllActiveSessions,
            get: getSession,
            activeCount: getActiveCount,
            kill: killSession,
            logs: getSessionLogs
        };

        return CrustSessions;

        function getAllSessions(pageSize, page, searchFilter,
                                start_from, start_to, command,
                                remote_user, server_account, server,
                                ordering){
            return $http.get(
                '/api/v1/crustsessions/',{
                    params: {
                        page_size: pageSize, page: page, created_at__gte:start_from,
                        created_at__lte:start_to, search_filter: searchFilter,
                        crustsessionevent__content__icontains:command,
                        remoteuser:remote_user, serveraccount__icontains:server_account,
                        server:server, ordering:ordering
                    }
                }
            );
        }

        function getAllActiveSessions(pageSize, page, searchFilter, ordering){
            return $http.get(
                '/api/v1/crustsessions/',{
                    params: {page_size: pageSize, page: page, active: 1,
                             search_filter: searchFilter, ordering:ordering}
                }
            );
        }

        function getSession(session_id){
            return $http.get('/api/v1/crustsessions/'+session_id+'/');
        }

        function getActiveCount(){
            return $http.get('/api/v1/crustsessions/active/count/');
        }

        function killSession(session_id){
            return $http.get('/api/v1/crustsessions/kill/',{
                params: {session_id:session_id}});
        }

        function getSessionLogs(session_id, pageSize, page, last_event_id){
            return $http.get(
                '/api/v1/crustsessions/'+session_id+'/log/',
                {params:{page_size: pageSize, page:page, last_event_id:last_event_id}}
            );
        }
    }

})();
