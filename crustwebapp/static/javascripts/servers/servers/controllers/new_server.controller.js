(function (){
    'use strict';

    angular
        .module('crust.servers.servers.controllers')
        .controller('NewServerController', NewServerController);

    NewServerController.$inject = [
        '$rootScope', '$scope', 'Servers',
        'ServerGroups', 'Snackbar'
    ];

    function NewServerController($rootScope, $scope, Servers, ServerGroups, Snackbar){
        var vm = this;

        vm.submit = submit;
        getServerGroups();

        function getServerGroups(){
            ServerGroups.all().then(getSGSuccess, getSGError);
            function getSGSuccess(data, status, headers, config){
                $scope.servergroups_data = data.data;
            }
            function getSGError(data, status, headers, config){
                Snackbar.error('Can not get Server Groups');
            }
        }


        function submit(){
            console.log(vm.server_group);
            Servers.create({
                server_name: vm.server_name, server_ip: vm.server_ip,
                comment: vm.comment, sshv2_port: vm.sshv2_port,
                telnet_port: vm.telnet_port, server_group: vm.server_group
            }).then(submitSuccess, submitError);

            function submitSuccess(data, status, headers, config){
                Snackbar.show('New Server Created Successfuly.');
                $rootScope.$broadcast('server.created');
                $scope.closeThisDialog();
            }
            function submitError(data, status, headers, config){
                Snackbar.error(
                    'Can not create Server. Check Input.',
                    {errors:data.data});
            }
        }

    }

})();
