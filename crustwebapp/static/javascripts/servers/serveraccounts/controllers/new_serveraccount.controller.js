(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts.controllers')
        .controller('NewServerAccountController', NewServerAccountController);

    NewServerAccountController.$inject = [
        '$rootScope', '$scope', 'ServerGroups',
        'ServerAccounts', 'Servers', 'Snackbar'
    ];

    function NewServerAccountController($rootScope, $scope, ServerGroups,
                                        ServerAccounts, Servers, Snackbar){
        var vm = this;

        vm.submit = submit;
        $scope.selected_server_groups = [];
        vm.assign_server_group = null;
        vm.assign_mode='server';
        $scope.protocol_data = ['ssh', 'telnet'];
        vm.getServersSuggestion = getServersSuggestion;
        vm.getServerGroupsSuggestion = getServerGroupsSuggestion;
        //getServers();


        $scope.onServerGroupSelect = function($item, $model, $label){
            console.log($item);
            console.log($label);
            $scope.selected_server_groups.push($item);
            vm.assign_server_group = null;
        };
        $scope.removeSG = function(index){
            $scope.selected_server_groups.splice(index, 1);
        };



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


        function getServerGroupsSuggestion($viewValue){
            return ServerGroups.getSuggestion($viewValue).then(
                getSGSuccess, getSGError
            );
            function getSGSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getSGError(data, status, headers, config){
                Snackbar.error('Can not get Server Groups');
            }
        }

        function submit(){
            console.log(vm.server);
            console.log(vm.assign_mode);

            ServerAccounts.create({
                username: vm.username, password: vm.password,
                confirm_password: vm.confirm_password, is_locked: vm.is_locked,
                comment: vm.comment, server: vm.server, protocol: vm.protocol,
                sshv2_private_key: vm.sshv2_private_key,
                assign_mode:vm.assign_mode, server_groups:$scope.selected_server_groups
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
