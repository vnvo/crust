(function (){
    'use strict';

    angular
        .module('crust.remoteusers.services')
        .factory('RemoteUsers', RemoteUsers);

    RemoteUsers.$inject = ['$http'];

    function RemoteUsers($http){
        var RemoteUsers = {
            all: getAllRemoteUsers,
            get: getRemoteUser,
            create: createRemoteUser,
            update: updateRemoteUser,
            delete: deleteRemoteUser,
            count: getCount
        };

        return RemoteUsers;


        function getAllRemoteUsers(){
            return $http.get('/api/v1/remoteusers/');
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
