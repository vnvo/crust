(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts.controllers')
        .controller('UpdateServerAccountController', UpdateServerAccountController);

    UpdateServerAccountController.$inject = [
        '$rootScope', '$scope', 'ServerAccounts',
        'Servers', 'Snackbar', 'ServerGroups'
    ];

    function UpdateServerAccountController(
        $rootScope, $scope, ServerAccounts,
        Servers, Snackbar, ServerGroups){

        var vm = this;
        vm.update = update;
        $scope.selected_server_groups = [];
        $scope.remove_server_groups = [];

        vm.assign_server_group = null;
        vm.assign_mode='server';
        vm.password_mode = 'local';
        $scope.protocol_data = ['ssh', 'telnet'];
        $scope.password_modes = ['local', 'ask user'];
        vm.getServersSuggestion = getServersSuggestion;
        vm.getServerGroupsSuggestion = getServerGroupsSuggestion;

        getServerAccountInfo();

        $scope.onServerGroupSelect = function($item, $model, $label){
            console.log($item);
            console.log($label);
            $scope.selected_server_groups.push($item);
            vm.assign_server_group = null;
        };
        $scope.removeSG = function(index){
            var item = $scope.selected_server_groups.splice(index, 1);
            $scope.remove_server_groups.push(item[0]['id']);
            console.log($scope.remove_server_groups);
        };


        function getServersSuggestion($viewValue){
            return Servers.getSuggestion($viewValue).then(
                getServersSuccess, getServersError);
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

        function getServerAccountInfo(){
            ServerAccounts.get(
                $scope.update_serveraccount_id
            ).then(getSASuccess, getSAError);

            function getSASuccess(data, status, headers, config){
                var sa_data = data.data;
                vm.serveraccount_id = sa_data.id;
                vm.username = sa_data.username;
                vm.password_mode = sa_data.password_mode;
                vm.server = sa_data.server;
                vm.protocol = sa_data.protocol;
                vm.sshv2_private_key = sa_data.sshv2_private_key;
                vm.is_locked = sa_data.is_locked;
                vm.comment = sa_data.comment;

                if(vm.server==null){
                    vm.assign_mode='server-group';
                    getAccountServerGroups();
                }
            }

            function getAccountServerGroups(){
                ServerAccounts.getAccountGroups(vm.serveraccount_id).then(
                    getSGASuccess, getSGAError);
                function getSGASuccess(data, status, heders, config){
                    console.log(data.data.results);
                    angular.forEach(data.data.results,
                                    function(sga, index){
                                        console.log(index);
                                        console.log(sga);
                                        $scope.selected_server_groups.push(
                                            sga.server_group
                                        );
                                    }
                                   );
                }
                function getSGAError(data, status, headers, config){
                    console.log(data);
                }
            }

            function getSAError(data, status, headers, config){
                Snackbar.error('Can not get Server Account Info');
            }
        }

        function update(){
            ServerAccounts.update(
                vm.serveraccount_id,
                {username: vm.username, password: vm.password, assign_mode:vm.assign_mode,
                 confirm_password: vm.confirm_password, is_locked: vm.is_locked,
                 comment: vm.comment, sshv2_private_key: vm.ssh2_private_key,
                 server: vm.server, protocol: vm.protocol, password_mode:vm.password_mode,
                 server_groups:$scope.selected_server_groups
                }
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
