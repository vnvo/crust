/**
 * ServerGroups
 * @namespace crust.servers.server_groups.directives
 */

(function() {
    'use strict';

    angular
        .module('crust.servers.server_groups.directives')
        .directive('servergroups', servergroups);

    /**
     * @namespace servergroups
     */
    function servergroups(){
        /**
         * @name servergroups
         * @desc The directive to render ServerGroups
         * @memberOf crust.servers.server_groups.directives.servergroups
         */
        var servergroups_directive = {
            controller: 'ServerGroupsController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                server_groups: '='
            },
            templateUrl: '/static/templates/servers/server_groups/servergroups.directive.html'
        };

        return servergroups_directive;
    }

})();
