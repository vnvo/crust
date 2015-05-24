(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts.services')
        .factory('ServerAccounts', ServerAccounts);

    ServerAccounts.$inject = ['$http'];

    function ServerAccounts($http){
        var ServerAccounts = {
            all: getAllServerAccounts,
            get: getServerAccount,
            count: getCount,
            create: createServerAccount,
            update: updateServerAccount,
            delete: deleteServerAccount
        };
        return ServerAccounts;

        function getAllServerAccounts(){
            return $http.get('/api/v1/serveraccounts/');
        }

        function getServerAccount(serveraccount_id){
            return $http.get('/api/v1/serveraccounts/'+serveraccount_id+'/');
        }

        function getCount(){
            return $http.get('/api/v1/serveraccounts/count/');
        }

        function createServerAccount(serveraccount_info){
            return $http.post(
                '/api/v1/serveraccounts/', serveraccount_info);
        }

        function updateServerAccount(serveraccount_id, serveraccount_info){
            return $http.put(
                '/api/v1/serveraccounts/'+serveraccount_id+'/',
                serveraccount_info
            );
        }

        function deleteServerAccount(serveraccount_id){
            return $http.delete('/api/v1/serveraccounts/'+serveraccount_id+'/');
        }
    }

})();
