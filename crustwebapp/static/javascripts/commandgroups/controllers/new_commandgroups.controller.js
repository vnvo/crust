(function (){
    'use strict';

    angular
        .module('crust.commandgroups.controllers')
        .controller('NewCommandGroupController', NewCommandGroupController);

    NewCommandGroupController.$inject = [
        '$rootScope', '$scope', 'CommandGroups', 'Snackbar'
    ];

    function NewCommandGroupController($rootScope, $scope, CommandGroups, Snackbar){
        var vm = this;

        vm.submit = submit;

        function submit(){
            CommandGroups.create(
                {command_group_name: vm.command_group_name,
                 default_action: (vm.default_action==true ? 'allow' : 'deny'),
                 comment: vm.comment}
            ).then(createCGSuccess, createCGError);

            function createCGSuccess(data, status, headers, config){
                Snackbar.show('Command Groups Created Successfuly.');
                $rootScope.$broadcast('commandgroup.created');
                $scope.closeThisDialog();
            }
            function createCGError(data, status, headers, config){
                Snackbar.error('Can not create Command Group, Check Input.');
            }
        }

    }

})();
