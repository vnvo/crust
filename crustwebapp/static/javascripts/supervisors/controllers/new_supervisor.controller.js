/*
 * @namespace NewSupervisorController
 */
(function(){
    'use strict';

    angular
        .module('crust.supervisors.controllers')
        .controller('NewSupervisorController', NewSupervisorController);

    NewSupervisorController.$inject = [
        '$rootScope', '$scope', 'Supervisors', 'Snackbar'
    ];

    function NewSupervisorController($rootScope, $scope, Supervisors, Snackbar){
        var vm = this;

        vm.submit = submit;

        function submit(){

            Supervisors.create(
                vm.username, vm.password, vm.email, vm.is_admin, vm.is_active
            ).then(submitSuccess, submitError);

            function submitSuccess(data, status, headers, config){
                Snackbar.show('Supervisor '+vm.username+' created successfuly.');
                $rootScope.$broadcast('supervisor.created');
                $scope.closeThisDialog();
            }

            function submitError(data, status, headers, config){
                console.log(data);
                console.log(status);
                Snackbar.error('Can not create Supervisor', {errors: data});
            }
        }
    }

})();
