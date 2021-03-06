(function() {
    'use strict';

    angular
        .module('crust.servers.server_groups.controllers')
        .controller('NewServerGroupController', NewServerGroupController);

    NewServerGroupController.$inject = [
        '$scope', 'ServerGroups', 'Snackbar',
        'Supervisors', 'Authentication', '$rootScope'
    ];

    function NewServerGroupController($scope, ServerGroups, Snackbar, Supervisors, Authentication, $rootScope){
        var vm = this;

        vm.submit = submit;
        vm.getSupervisorsSuggestion = getSupervisorsSuggestion;

        if(Authentication.isAdmin()){
            Supervisors.all().then(
                function(data, status, headers, config){
                    $scope.supervisors = data.data.results;
                    vm.selected_supervisor = null;
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
        function submit(){
            ServerGroups.create(
                vm.group_name, vm.selected_supervisor
            ).then(createSuccessFn, createErrorFn);

            function createSuccessFn(data, status, header, config){
                $rootScope.$broadcast('servergroup.created');
                $scope.closeThisDialog();
                Snackbar.show('Server Group Created Successfuly');
            }
            function createErrorFn(data, status, header, config){
                Snackbar.error('Create Server Group Error', {errors:data.data});
            }
        }
    }
})();
