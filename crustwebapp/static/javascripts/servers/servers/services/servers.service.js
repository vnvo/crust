(function (){
    'use strict';

    angular
        .module('crust.servers.servers.services')
        .factory('Servers', Servers);

    Servers.$inject = ['$http'];

    /**
     * @namespace Servers
     * @returns {Factory}
     */
    function Servers($http){
        var Servers = {
            all: getAllServers,
            getSuggestion: getServersSuggestion,
            get: getServer,
            count: getCount,
            create: createServer,
            update: updateServer,
            delete: deleteServer
        };

        return Servers;

        function getAllServers(){
            return $http.get('/api/v1/servers/');
        }

        function getServersSuggestion(hint){
            return $http.get(
                '/api/v1/servers/',{
                    params: {hint:hint}
                }
            );
        }

        function getServer(server_id){
            return $http.get('/api/v1/servers/'+server_id+'/');
        }

        function getCount(){
            return $http.get('/api/v1/servers/count/');
        }

        /**
         * @name create
         * @desc create a new server based on server_info object
         * @param {object} server_info:
         *        server_group, server_name, server_ip,
         *        timeout, sshv2_port, telnet_port, comment
         */
        function createServer(server_info){
            return $http.post(
                '/api/v1/servers/', server_info
            );
        }

        function updateServer(server_id, server_info){
            return $http.put(
                '/api/v1/servers/'+server_id+'/',
                server_info
            );
        }

        function deleteServer(server_id){
            return $http.delete('/api/v1/servers/'+server_id+'/');
        }

    }

})();
