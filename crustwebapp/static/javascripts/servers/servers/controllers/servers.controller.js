/*
 * @namespace ServersController
 */
(function (){
    'use strict';

    angular
        .module('crust.servers.servers.controllers')
        .controller('ServersController', ServersController);

    ServersController.$inject = [
        '$scope', 'Servers', 'Snackbar',
        'ngDialog', 'ServerGroups', '$location'
    ];


    function ServersController($scope, Servers, Snackbar,
                               ngDialog, ServerGroups, $location){
        var vm = this;
        console.log($location.search().server_group);
        $scope.deleteServer = deleteServer;
        $scope.startUpdateDialog = startUpdateDialog;
        vm.server_group_filter = null;
        vm.ip_filter = null;

        $scope.$watch('vm.server_group_filter',
                      function (newVal, oldVal) {
                          if (newVal !== oldVal)
                              getServers();
                      }, true);
        $scope.$watch('vm.ip_filter',
                      function (newVal, oldVal) {
                          if (newVal !== oldVal)
                              getServers();
                      }, true);

        getServerGroups();
        if($location.search().server_group)
            setServerGroupFilter($location.search().server_group);


        function setServerGroupFilter(server_group_id){
            ServerGroups.get(server_group_id).then(
                function(data, status, headers, config){
                    vm.server_group_filter = data.data;
                },
                function(data, status, headers, config){
                    console.log('Could not load server group: '+server_group_id);
                }
            );
        }

        function getServerGroups(){
            ServerGroups.all(200, 1).then(getSGSuccess, getSGError);
            function getSGSuccess(data, status, headers, config){
                vm.servergroups_data = data.data.results;
            }
            function getSGError(data, status, headers, config){
                Snackbar.error('Can not get Server Groups');
            }
        }


        function startUpdateDialog(event, grid_row){
            $scope.update_server_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/servers/servers/update_server.templ.html',
                controller: 'UpdateServerController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        function deleteServer(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a Server, are you sure?')){
                return;
            }

            Servers.delete(
                grid_row.entity.id
            ).then(deleteServerSuccess, deleteServerError);

            function deleteServerSuccess(data, status, headers, config){
                Snackbar.show('Server Deleted Successfuly.');
                getServers();
            }
            function deleteServerError(data, status, headers, config){
                Snackbar.error('Could not delete the Server.');
            }
        }


        // listen for creation/update events
        $scope.$on(
            'server.created',
            function(){ getServers(); }
        );
        $scope.$on(
            'server.updated',
            function(){ getServers(); }
        );

        // Init/config ngGrid instance
        $scope.totalServerItems = 0;
        $scope.pagingOptions = {
            pageSizes: [5, 10, 20, 50],
            pageSize: 10,
            currentPage: 1
        };

        $scope.filterText = null;
        $scope.filterOptions = {
            filterText: $scope.filterText,
            useExternalFilter: true
        };

        $scope.sortOptions = {
            fields: ['id'],
            directions: ['desc']
        };

        $scope.setPagingData = function(data, page, pageSize){
            var pagedData = data.results;
            $scope.servers_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText,
                                             ordering, serverGroup, ip) {
            setTimeout(function () {
                var data;

                Servers.all(pageSize, page, searchText,
                            ordering, serverGroup, ip).then(
                                getAllServersSuccess, getAllServersError
                            );
                function getAllServersSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllServersError(data, status, headers, config){
                    Snackbar.error('Can not get Servers data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getServers();
            }
        }, true);

        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getServers();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                console.log($scope.sortOptions.fields);
                console.log($scope.sortOptions.directions);
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');

                getServers();
            }
        }, true);


        $scope.gridOptions = {
            data: 'servers_data',
            rowHeight: 35,
            enablePaging: true,
            showHeader: true,
            showFooter: true,
            showGroupPanel: true,
            showFilter: true,
            multiSelect: false,
            useExternalSorting: true,
            sortInfo: $scope.sortOptions,
            totalServerItems: "totalServerItems",
            columnDefs: [
                {displayName:'#', width: 30,
                 cellTemplate: '<div class="ngCellText" data-ng-class="col.colIndex()"><span>{{row.rowIndex + 1}}</span></div>'
                },
                {field: 'id', displayName: 'ID', width: 35},
                {field: 'server_name', displayName: 'Server Name', width: 145},
                {field: 'server_ip', displayName: 'IP', width: 110},
                {field: 'server_group.group_name', displayName: 'Server Group', width: 110},
                {field: 'sshv2_port', displayName: 'SSHv2 Port', width: 90},
                {field: 'telnet_port', displayName: 'Telnet Port', width: 90},
                {field: 'serveraccount_count', displayName:'Accounts #', width: 90},
                {field: 'timeout', displayName: 'Timeout', width: 70},
                {field: 'comment', displayName: 'Comment', width: 150},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/servers/servers/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getServers(){
            var server_group_id = null;
            if(vm.server_group_filter)
                server_group_id=vm.server_group_filter['id'];

            console.log(server_group_id);
            console.log(vm.ip_filter);

            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering,
                server_group_id,
                vm.ip_filter
            );
        }

    }

})();
