(function (){
    'use strict';

    angular
        .module('crust.servers.servers.controllers')
        .controller('UpdateServerController', UpdateServerController);

    UpdateServerController.$inject = [
        '$rootScope', '$scope', 'Snackbar',
        'Servers', 'ServerGroups'
    ];

    function UpdateServerController($rootScope, $scope, Snackbar, Servers, ServerGroups){
        var vm = this;

        vm.update = update;
        getServerGroups();
        getServerInfo();

        function getServerGroups(){
            ServerGroups.all(100,1).then(getSGSuccess, getSGError);
            function getSGSuccess(data, status, headers, config){
                $scope.servergroups_data = data.data.results;
            }
            function getSGError(data, status, headers, config){
                Snackbar.error('Can not get Server Groups');
            }
        }

        function getServerInfo(){
            Servers.get($scope.update_server_id).then(
                getServerSuccess, getServerError
            );

            function getServerSuccess(data, status, headers, config){
                var s_data = data.data;
                vm.server_id = s_data.id;
                vm.server_name = s_data.server_name;
                vm.server_ip = s_data.server_ip;
                vm.server_group = s_data.server_group;
                vm.sshv2_port = s_data.sshv2_port;
                vm.telnet_port = s_data.telnet_port;
                vm.timeout = s_data.timeout;
                vm.comment = s_data.comment;
            }
            function getServerError(data, status, headers, config){
                Snackbar.error('Can not get Server Info.');
            }
        }

        function update(){
            Servers.update(
                vm.server_id,{
                    server_name: vm.server_name, server_ip: vm.server_ip,
                    server_group: vm.server_group, sshv2_port: vm.sshv2_port,
                    telnet_port: vm.telnet_port, comment: vm.comment,
                    timeout: vm.timeout
                }
            ).then(updateSuccess, updateError);

            function updateSuccess(data, status, headers, config){
                Snackbar.show('Server Updated Successfuly.');
                $rootScope.$broadcast('server.updated');
                $scope.closeThisDialog();
            }
            function updateError(data, status, headers, config){
                Snackbar.error('Can not update Server. Check Input');
            }
        }
    }


})();
