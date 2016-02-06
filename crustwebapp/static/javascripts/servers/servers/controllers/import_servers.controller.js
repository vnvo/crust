(function (){
    'use strict';

    angular
        .module('crust.servers.servers.controllers')
        .controller('ImportServersController', ImportServersController);

    ImportServersController.$inject = [
        '$rootScope', '$scope', 'Servers', 'ServerGroups', 'Snackbar'
    ];


    function ImportServersController($rootScope, $scope, Servers, ServerGroups, Snackbar){
        var vm = this;
        vm.submitFile = submitFile;
        vm.importing = false;
        vm.import_messages = ['Started...'];
        $scope.csvContent = '';
        vm.csv_header = null;
        vm.total_entries = 0;
        vm.done_entries = 0;

        function importEntry(entry){
            if(!entry.length || entry[0]==''){
                vm.done_entries += 1;
                vm.import_messages.push('Finished');
                $rootScope.$broadcast('server.created');
                return;
            }
            var server_info = vm.csv_header.reduce(
                function(prev, info_key, i){
                    var val = entry[i];
                    if(val==undefined)
                        val='';       
                    val = val.replace(/(?:\\[rn]|[\r\n]+)+/g, "");
                    if(info_key=='sshv2_port')
                        val = (val.length ? parseInt(val):22);
                    if(info_key=='telnet_port')
                        val = (val.length ? parseInt(val):23);

                    info_key = info_key.replace(/(?:\\[rn]|[\r\n]+)+/g, "");
                    prev[info_key]=val;
                    return prev;
                }, {}
            );
            Servers.create(server_info).then(
                function(data, status, headers, config){
                    vm.done_entries += 1;
                    if(vm.entries.length && vm.entries!= [""])
                        importEntry(vm.entries.shift().split(','));
                },
                function(data, status, headers, config){
                    vm.import_messages.push(
                        'Error on '+server_info['server_name']
                    );
                    if(vm.entries.length)
                        importEntry(vm.entries.shift().split(','));
                    else{
                        vm.import_messages.push('Finished.');
                        $rootScope.$broadcast('server.created');
                    }
                }
            );
        }

        function submitFile(){
            vm.entries = $scope.csvContent.split('\n');
            vm.total_entries = vm.entries.length-1;
            vm.importing = true;
            vm.csv_header = vm.entries.shift().split(',');
            console.log(vm.csv_header);
            //kick off importing
            importEntry(vm.entries.shift().split(','));
        }
    }
})();
