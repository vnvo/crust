(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts.controllers')
        .controller('NewServerAccountController', NewServerAccountController);

    NewServerAccountController.$inject = [
        '$rootScope', '$scope', 'ServerAccounts',
        'Servers', 'Snackbar'
    ];

    function NewServerAccountController($rootScope, $scope,
                                        ServerAccounts, Servers, Snackbar){
        var vm = this;

        vm.submit = submit;
        $scope.protocol_data = ['ssh', 'telnet', 'ssh and telnet'];
        vm.getServersSuggestion = getServersSuggestion;
        //getServers();

        function getServersSuggestion($viewValue){
            return Servers.getSuggestion($viewValue).then(
                getServersSuccess, getServersError
            );
            function getServersSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getServersError(data, status, headers, config){
                Snackbar.error('Can not get Servers');
            }
        }


        function submit(){
            console.log(vm.server);
            ServerAccounts.create({
                username: vm.username, password: vm.password,
                confirm_password: vm.confirm_password, is_locked: vm.is_locked,
                comment: vm.comment, server: vm.server, protocol: vm.protocol,
                sshv2_private_key: vm.sshv2_private_key
            }).then(submitSuccess, submitError);

            function submitSuccess(data, status, headers, config){
                Snackbar.show('New Server Account Created Successfuly.');
                $rootScope.$broadcast('serveraccount.created');
                $scope.closeThisDialog();
            }
            function submitError(data, status, headers, config){
                Snackbar.error('Can not create Server Account. Check Input.');
            }
        }
    }

})();
