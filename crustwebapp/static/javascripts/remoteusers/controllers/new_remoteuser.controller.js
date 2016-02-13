(function (){
    'use strict';

    angular
        .module('crust.remoteusers.controllers')
        .controller('NewRemoteUserController', NewRemoteUserController);

    NewRemoteUserController.$inject = [
        '$rootScope', '$scope', 'RemoteUsers', 'Snackbar'
    ];

    function NewRemoteUserController($rootScope, $scope, RemoteUsers, Snackbar){
        var vm = this;

        vm.auth_modes = ['local', 'ldap'];
        vm.submit = submit;

        function submit(){
            RemoteUsers.create(
                {username: vm.username, password: vm.password, allow_ip:vm.allow_ip,
                 is_locked: vm.is_locked, sshv2_public_key: vm.sshv2_public_key,
                 comment: vm.comment, email: vm.email, cell_phone: vm.cell_phone,
                 auth_mode: vm.auth_mode
                }
            ).then(submitRuSuccess, submitRuError);

            function submitRuSuccess(data, status, headers, config){
                Snackbar.show('New Remote User Created Successfuly.');
                $rootScope.$broadcast('remoteuser.created');
                $scope.closeThisDialog();
            }
            function submitRuError(data, status, headers, config){
                Snackbar.error('Can not create new Remote User');
            }
        }
    }

})();
