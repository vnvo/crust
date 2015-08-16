(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts.services')
        .factory('ServerAccounts', ServerAccounts);

    ServerAccounts.$inject = ['$http'];

    function ServerAccounts($http){
        var ServerAccounts = {
            all: getAllServerAccounts,
            getSuggestion: getServerSuggestion,
            get: getServerAccount,
            count: getCount,
            create: createServerAccount,
            update: updateServerAccount,
            delete: deleteServerAccount
        };
        return ServerAccounts;

        function getAllServerAccounts(page_size, page, filterText, ordering){
            return $http.get('/api/v1/serveraccounts/',{
                params: {page_size:page_size, page:page,
                         search_filter: filterText, ordering: ordering}
            });
        }

        function getServerSuggestion(hint){
            return $http.get(
                '/api/v1/serveraccounts/', {
                    params: {hint:hint}
                }
            );
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
