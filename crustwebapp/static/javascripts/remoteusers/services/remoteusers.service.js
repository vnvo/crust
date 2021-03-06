(function (){
    'use strict';

    angular
        .module('crust.remoteusers.services')
        .factory('RemoteUsers', RemoteUsers);

    RemoteUsers.$inject = ['$http'];

    function RemoteUsers($http){
        var RemoteUsers = {
            all: getAllRemoteUsers,
            getSuggestion: getRemoteUsersSuggestion,
            get: getRemoteUser,
            create: createRemoteUser,
            update: updateRemoteUser,
            delete: deleteRemoteUser,
            count: getCount
        };

        return RemoteUsers;


        function getAllRemoteUsers(page_size, page, searchFilter, ordering){
            return $http.get('/api/v1/remoteusers/', {
                params: {page_size: page_size, page:page,
                         search_filter: searchFilter,
                         ordering: ordering}
            });
        }

        function getRemoteUsersSuggestion(hint){
            return $http.get(
                '/api/v1/remoteusers/',{
                    params: {hint: hint}
                }
            );
        }

        function getRemoteUser(remoteuser_id){
            return $http.get('/api/v1/remoteusers/'+remoteuser_id+'/');
        }

        function createRemoteUser(remoteuser_info){
            return $http.post('/api/v1/remoteusers/', remoteuser_info);
        }

        function updateRemoteUser(remoteuser_id, remoteuser_info){
            return $http.put(
                '/api/v1/remoteusers/'+remoteuser_id+'/',
                remoteuser_info
            );
        }

        function deleteRemoteUser(remoteuser_id){
            return $http.delete('/api/v1/remoteusers/'+remoteuser_id+'/');
        }

        function getCount(){
            return $http.get('/api/v1/remoteusers/count/');
        }
    }

})();
