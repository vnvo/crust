/**
 * @namespace UpdateSupervisorController
 */
(function(){
    'use strict';

    angular
        .module('crust.supervisors.controllers')
        .controller('UpdateSupervisorController', UpdateSupervisorController);

    UpdateSupervisorController.$inject = [
        '$rootScope', '$scope', 'Supervisors', 'Snackbar'
    ];

    function UpdateSupervisorController($rootScope, $scope, Supervisors, Snackbar){
        var vm = this;

        vm.update = update;
        getSupervisorInfo();

        function getSupervisorInfo(){
            Supervisors.get(
                $scope.update_supervisor_id
            ).then(getSupSuccess, getSupError);

            function getSupSuccess(data, status, headers, config){
                $scope.sup_info = data.data;
                // Set default values
                vm.supervisor_id = data.data.id;
                vm.username = data.data.username;
                vm.email = data.data.email;
                vm.is_admin = data.data.is_admin;
                vm.is_active = data.data.is_active;
            }
            function getSupError(data, status, headers, config){
                Snackbar.error('Error: can not get Supervisor Info.');
                $scope.closeThisDialog();
            }
        }

        function update(){
            Supervisors.update(
                vm.supervisor_id,
                {username: vm.username, password: vm.password,
                 confirm_password: vm.confirm_password, email: vm.email,
                 is_admin: vm.is_admin, is_active: vm.is_active}
            ).then(updateSupSuccess, updateSupError);

            function updateSupSuccess(data, status, headers, config){
                Snackbar.show('Supervisor Updated Successfuly.');
                $rootScope.$broadcast('supervisor.updated');
                $scope.closeThisDialog();
            }
            function updateSupError(data, status, headers, config){
                Snackbar.error('Error: can not update Supervisor');
            }
        }
    }
})();
