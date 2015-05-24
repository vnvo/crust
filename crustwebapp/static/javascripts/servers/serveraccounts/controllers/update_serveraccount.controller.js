(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts.controllers')
        .controller('UpdateServerAccountController', UpdateServerAccountController);

    UpdateServerAccountController.$inject = [
        '$rootScope', '$scope', 'ServerAccounts',
        'Servers', 'Snackbar'
    ];

    function UpdateServerAccountController($rootScope, $scope,
                                           ServerAccounts, Servers, Snackbar){
        var vm = this;
        vm.update = update;
        $scope.protocol_data = ['ssh', 'telnet', 'ssh and telnet'];

        getServers();
        getServerAccountInfo();

        function getServers(){
            Servers.all().then(getServersSuccess, getServersError);
            function getServersSuccess(data, status, headers, config){
                $scope.servers_data = data.data;
            }
            function getServersError(data, status, headers, config){
                Snackbar.error('Can not get Servers');
            }
        }

        function getServerAccountInfo(){
            ServerAccounts.get(
                $scope.update_serveraccount_id
            ).then(getSASuccess, getSAError);

            function getSASuccess(data, status, headers, config){
                var sa_data = data.data;
                vm.serveraccount_id = sa_data.id;
                vm.username = sa_data.username;
                vm.server = sa_data.server;
                vm.protocol = sa_data.protocol;
                vm.sshv2_private_key = sa_data.sshv2_private_key;
                vm.is_locked = sa_data.is_locked;
                vm.comment = sa_data.comment;
            }
            function getSAError(data, status, headers, config){
                Snackbar.error('Can not get Server Account Info');
            }
        }

        function update(){
            ServerAccounts.update(
                vm.serveraccount_id,
                {username: vm.username, password: vm.password,
                 confirm_password: vm.confirm_password, is_locked: vm.is_locked,
                 comment: vm.comment, sshv2_private_key: vm.ssh2_private_key,
                 server: vm.server, protocol: vm.protocol}
            ).then(updateSASuccess, updateSAError);

            function updateSASuccess(data, status, heders, config){
                Snackbar.show('Server Account Updated Successfuly.');
                $rootScope.$broadcast('serveraccount.updated');
                $scope.closeThisDialog();
            }
            function updateSAError(data, status, headers, config){
                Snackbar.error('Can not update Server Account.');
            }
        }
    }

})();
