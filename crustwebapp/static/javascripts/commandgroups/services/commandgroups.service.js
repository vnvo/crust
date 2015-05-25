(function (){
    'use strict';

    angular
        .module('crust.commandgroups.services')
        .factory('CommandGroups', CommandGroups);

    CommandGroups.$inject = ['$http'];

    function CommandGroups($http){
        var CommandGroups = {
            all: getAllCommandGroups,
            get: getCommandGroup,
            count: getCGCount,
            create: createCommandGroup,
            update: updateCommandGroup,
            delete: deleteCommandGroup
        };

        return CommandGroups;

        function getAllCommandGroups(){
            return $http.get('/api/v1/commandgroups/');
        }

        function getCommandGroup(commandgroup_id){
            return $http.get('/api/v1/commandgroups/'+commandgroup_id+'/');
        }

        function getCGCount(){
            return $http.get('/api/v1/commandgroups/count/');
        }

        function createCommandGroup(commandgroup_info){
            return $http.post(
                '/api/v1/commandgroups/',
                commandgroup_info
            );
        }

        function updateCommandGroup(commandgroup_id, commandgroup_info){
            return $http.put(
                '/api/v1/commandgroups/'+commandgroup_id+'/',
                commandgroup_info
            );
        }

        function deleteCommandGroup(commandgroup_id){
            return $http.delete('/api/v1/commandgroups/'+commandgroup_id+'/');
        }
    }

})();
