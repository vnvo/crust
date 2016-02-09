(function (){
    'use strict';

    angular
        .module('crust.remoteusers.controllers')
        .controller('UpdateRemoteUserController', UpdateRemoteUserController);

    UpdateRemoteUserController.$inject = [
        '$rootScope', '$scope', 'RemoteUsers', 'Snackbar'
    ];

    function UpdateRemoteUserController($rootScope, $scope, RemoteUsers, Snackbar){

        var vm = this;

        vm.update = update;

        getRemoteUserInfo();

        function getRemoteUserInfo(){
            RemoteUsers.get(
                $scope.update_remoteuser_id
            ).then(getRuInfoSuccess, getRuInfoError);

            function getRuInfoSuccess(data, status, headers, config){
                var ru_data = data.data;
                vm.remoteuser_id = ru_data.id;
                vm.username = ru_data.username;
                vm.email = ru_data.email;
                vm.cell_phone = ru_data.cell_phone;
                vm.is_locked = ru_data.is_locked;
                vm.sshv2_public_key = ru_data.sshv2_public_key;
                vm.comment = ru_data.comment;
                vm.allow_ip = ru_data.allow_ip;
            }
            function getRuInfoError(data, status, headers, config){
                Snackbar.error('Can not get Remote User Info.');
            }
        }

        function update(){
            RemoteUsers.update(
                vm.remoteuser_id,
                {username: vm.username, password: vm.password,
                 is_locked: vm.is_locked, email: vm.email,
                 cell_phone: vm.cell_phone, comment: vm.comment,
                 sshv2_public_key: vm.sshv2_public_key, allow_ip:vm.allow_ip}
            ).then(updateRuSuccess, updateRuError);

            function updateRuSuccess(data, status, headers, config){
                Snackbar.show('Remote User Updated Successfuly.');
                $rootScope.$broadcast('remoteuser.updated');
                $scope.closeThisDialog();
            }
            function updateRuError(data, status, headers, config){
                Snackbar.error('Can not update Remote User, Check Input.');
            }
        }
    }

})();
