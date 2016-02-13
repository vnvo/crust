(function (){
    'use strict';

    angular
        .module('crust.remote_connections.services')
        .factory('RemoteConnections', RemoteConnections);

    RemoteConnections.$inject = ['$http'];

    function RemoteConnections($http){
        var RemoteConnections = {
            all: getAllRC,
            allActive: getAllActive,
            failStats: getFailedRCStats,
            failCount: getFailCount,
            userFailCount: getUserFailCount
        };

        return RemoteConnections;

        function getAllRC(page_size, page, search_filter, ordering){}

        function getAllActive(page_size, page, search_filter, ordering){
            return $http.get(
                '/api/v1/remoteconnections/', {
                    params: {
                        page_size:page_size, page:page, active:1,
                        search_filter:search_filter, ordering:ordering
                    }
                }
            );
        }

        function getFailedRCStats(page_size, page, search_filter, ordering){
            return $http.get(
                '/api/v1/remoteconnections/', {
                    params: {
                        page_size:page_size, page:page, successful:true,
                        search_filter:search_filter, ordering:ordering
                    }
                }
            );
        }

        function getFailCount(){
            return $http.get('/api/v1/remoteconnections/failcount/');
        }

        function getUserFailCount(){
            return $http.get('/api/v1/remoteconnections/usersfailcount/');
        }

    }
})();
