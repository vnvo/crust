(function() {
    'use strict';

    angular
        .module('crust.servers.server_groups.controllers')
        .controller('UpdateServerGroupController', UpdateServerGroupController);

    UpdateServerGroupController.$inject = [
        '$scope', 'ServerGroups', 'Snackbar',
        'Supervisors', 'Authentication', '$rootScope'
    ];

    function UpdateServerGroupController($scope, ServerGroups, Snackbar, Supervisors, Authentication, $rootScope){
        var vm = this;

        vm.update = update;
        vm.getSupervisorsSuggestion = getSupervisorsSuggestion;

        ServerGroups.get($scope.update_sg_id).then(
            function(data, status, headers, config){
                var sg_data = data.data;
                vm.selected_supervisor = sg_data.supervisor;
                vm.group_name = sg_data.group_name;
            },
            function(data, status, headers, config){
                Snackbar.error('Could not get Server Group Data');
            }
        );

        if(Authentication.isAdmin()){
            Supervisors.all().then(
                function(data, status, headers, config){
                    $scope.supervisors = data.data.results;
                    //vm.selected_supervisor = null;
                },
                function(data, status, headers, config){
                    $scope.supervisors = null;
                    vm.selected_supervisor = null;
                }
            );
        }

        function getSupervisorsSuggestion($viewValue){
            return Supervisors.getSuggestion($viewValue).then(
                getSupSuggestionSuccess, getSupSuggestionError
            );
            function getSupSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getSupSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Supervisors data.');
            }
        }

        /**
         * @name submit
         * @desc Create a new ServerGroups
         * @memberOf crust.servers.server_groups.controllers.NewServerGroupsController
         */
        function update(){
            ServerGroups.update(
                $scope.update_sg_id,
                vm.group_name,
                vm.selected_supervisor
            ).then(updateSGSuccessFn, updateSGErrorFn);

            function updateSGSuccessFn(data, status, header, config){
                $rootScope.$broadcast('servergroup.updated');
                $scope.closeThisDialog();
                Snackbar.show('Server Group Updated Successfuly');
            }
            function updateSGErrorFn(data, status, header, config){
                Snackbar.error('Update Server Group Error', {errors:data.data});
            }
        }
    }
})();
