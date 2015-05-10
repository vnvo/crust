(function() {
    'use strict';

    angular
        .module('crust.servers.server_groups.controllers')
        .controller('NewServerGroupController', NewServerGroupController);

    NewServerGroupController.$inject = [
        '$scope', 'ServerGroups', 'Snackbar'
    ];

    function NewServerGroupController($scope, ServerGroups, Snackbar){
        var vm = this;

        vm.submit = submit;

        /**
         * @name submit
         * @desc Create a new ServerGroups
         * @memberOf crust.servers.server_groups.controllers.NewServerGroupsController
         */
        function submit(){
            ServerGroups.create(
                vm.group_name
            ).then(createSuccessFn, createErrorFn);

            /**
             * @name createSuccessFn
             * @desc Show snackbar with success message
             */
            function createSuccessFn(data, status, header, config){
                Snackbar.show('Server Group Created Successfuly');
            }

            /**
             * @name createErrorFn
             * @desc Show snackbar with error message
             */
            function createErrorFn(data, status, header, config){
                Snackbar.error('Create Server Group Error: '+data.error);
            }
        }
    }
})();
