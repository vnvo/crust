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
            delete: deleteServerAccount,

            //Server Group Account API
            getAccountGroups: getServerGroupsForAccount,
            delAccountGroups: delServerGroupsForAccount,
            addAccountGroups: addServerGroupsForAccount,

            //Server Account Map API
            getAccountServers: getServersForAccount,
            delAccountServers: delServersForAccount,
            addAccountServers: addServersForAccount,
            //getAccountsForServer: getAccountsForServer
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


        //////////////
        function getServerGroupsForAccount(server_account_id){
            return $http.get('/api/v1/servergroupaccounts/',
                             {params: {server_account_id:server_account_id}});
        }

        function delServerGroupsForAccount(server_group_account_id){
            return $http.delete('/api/v1/servergroupaccounts/'+server_group_account_id+'/');
        }

        function addServerGroupsForAccount(server_account, server_group){
            return $http.post(
                '/api/v1/servergroupaccount/',
                {server_account:server_account, server_group:server_group}
            );
        }

        //////////////
        /*
         * Returns directly mapped servers for the given account id
         */
        function getServersForAccount(server_account_id){
            return $http.get('/api/v1/serveraccountmaps/',
                             {params: {server_account_id:server_account_id}});
        }

        function delServersForAccount(server_account_map_id){
            return $http.delete('/api/v1/serveraccountmaps/'+server_account_map_id+'/');
        }

        function addServersForAccount(server_account, server){
            return $http.post(
                '/api/v1/serveraccountmaps/',
                {server_account:server_account, server:server}
            );
        }

        /*
         Return all available accounts for a server either with direct map or
         from server group account map
         */
        function getAllAccountsForServer(server_id){
            return $http.get('/api/v1/allserveraccounts/',
                             {params: {server_id:server_id}});
        }


    }

})();
