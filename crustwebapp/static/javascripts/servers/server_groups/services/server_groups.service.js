/**
* @namespace crust.servers.server_groups.services
 */
(function(){
    'use strict';

    angular
        .module('crust.servers.server_groups.services')
        .factory('ServerGroups', ServerGroups);

    ServerGroups.$inject = ['$http'];

    /**
     * @namespace ServerGroups
     * @returns {Factory}
     */
    function ServerGroups($http){
        var ServerGroups = {
            all: allServerGroups,
            getSuggestion: getServerGroupsSuggestion,
            getCount: getCount,
            create: createServerGroup,
            get: getServerGroup,
            update: updateServerGroup,
            delete: deleteServerGroup
        };

        return ServerGroups;

        /**
         * @name allServerGroups
         * @desc Get all ServerGroups
         * @returns {Promise}
         * @memberOf crust.servers.server_groups.services.ServerGroups
         */
        function allServerGroups(pageSize, page, searchFilter, ordering){
            return $http.get('/api/v1/servergroups/', {
                params: {page_size: pageSize, page:page,
                         search_filter: searchFilter,
                         ordering:ordering}
            });
        }

        /**
         * @name getServerGroupsSuggestion
         * @desc Get Server Groups matching the hint
         * @returns {Promise}
         * @memberOf crust.servers.server_groups.services.ServerGroups
         */
        function getServerGroupsSuggestion(hint){
            return $http.get(
                '/api/v1/servergroups/',{
                    params: {hint:hint}}
            );
        }

        /**
         * @name getCount
         * @desc get current count of Server Groups
         * @returns {Promise}
         * @memberOf crust.servers.server_groups.services.ServerGroups
         */
        function getCount(){
            return $http.get('/api/v1/servergroups/count/');
        }

        /**
         * @name createServerGroup
         * @desc Create a new Server Group
         * @returns {Promise}
         * @memberOf crust.servers.server_groups.services.ServerGroups
         */
        function createServerGroup(group_name, supervisor){
            return $http.post(
                '/api/v1/servergroups/',
                {
                    group_name: group_name,
                    supervisor: supervisor
                });
        }

        /**
         * @name getServerGroup
         * @desc Get the information of the given Server Group
         * @param {Integer} server_group_id, Id of the ServerGroup
         * @returns {object}
         * @memberOf crust.servers.server_groups.services.ServerGroups
         */
        function getServerGroup(server_group_id){
            return $http.get('/api/v1/servergroups/'+server_group_id+'/');
        }

        /**
         * @name updateServerGroup
         * @desc Update an existing ServerGroup
         * @param {integer} Server Group Id
         * @returns {Promise}
         * memberOf crust.servers.server_groups.services.ServerGroups
         */
        function updateServerGroup(server_group_id, server_group_name, supervisor){
            return $http.put('/api/v1/servergroups/'+server_group_id+'/', {
                group_name: server_group_name, supervisor: supervisor
            });
        }

        /**
         * @name deleteServerGroup
         * @desc Delete a ServerGroup
         * @param {integer} ServerGroupId
         * @returns {Promise}
         * @memberOf crust.servers.server_groups.services.ServerGroups
         */
        function deleteServerGroup(server_group_id){
            return $http.delete('/api/v1/servergroups/'+server_group_id+'/');
        }
    }
})();
